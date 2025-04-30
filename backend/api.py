from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import ollama
import os
import tempfile
from dotenv import load_dotenv, dotenv_values
import base64

# Load environment variables
load_dotenv()
env_vars = dotenv_values()

# Initialize Flask app
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
    }}
)
# Constants
MAX_INPUT_LENGTH = 1000
MAX_NEW_TOKENS = 280
COLLECTION_NAME = "medical_docs"
VECTOR_SIZE = 1024  # mxbai-embed-large vector size
OLLAMA_MODEL = env_vars.get("OLLAMA_MODEL", "mxbai-embed-large:335m")

# Initialize Qdrant client
client = QdrantClient(
    url=env_vars.get("QDRANT_URL"),
    api_key=env_vars.get("QDRANT_API_KEY")
)

# Try to create collection if it doesn't exist
try:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        )
    )
except Exception:
    print("Collection already exists")

def ensure_ollama_model():
    """Ensure the Ollama model is available locally"""
    try:
        ollama.show(OLLAMA_MODEL)
    except Exception:
        print(f"Pulling Ollama model {OLLAMA_MODEL}... This may take a few minutes.")
        try:
            ollama.pull(OLLAMA_MODEL)
            print("Model pulled successfully!")
        except Exception as e:
            print(f"Failed to pull model: {str(e)}")
            raise

def get_embeddings(texts):
    """Get embeddings using local Ollama"""
    try:
        ensure_ollama_model()
        embeddings = []
        for text in texts:
            response = ollama.embeddings(model=OLLAMA_MODEL, prompt=text)
            embeddings.append(response['embedding'])
        return embeddings
    except Exception as e:
        print(f"Failed to get embeddings: {str(e)}")
        raise

def process_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def store_documents(texts, embeddings):
    points = []
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        points.append(
            models.PointStruct(
                id=i,
                vector=embedding,
                payload={"text": text}
            )
        )
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def search_documents(query, top_k=3):
    # Get query embedding
    query_embedding = get_embeddings([query])[0]
    
    # Search in Qdrant
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )
    
    # Extract relevant texts
    relevant_texts = [hit.payload["text"] for hit in search_result]
    return relevant_texts

def load_model():
    try:
        # Using a smaller model that works on CPU
        model_name = "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ"
        
        # Load model and tokenizer with CPU and memory optimizations
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float32,  # Use float32 for CPU
            low_cpu_mem_usage=True,
            max_memory={'cpu': '450MB'},
            offload_folder="/tmp/offload"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        tokenizer.pad_token = tokenizer.eos_token
        model.eval()

        return model, tokenizer
    except Exception as e:
        print(f"Failed to load model: {str(e)}")
        return None, None

# Load model once at startup
model, tokenizer = load_model()

def generate_prompt(question, pdf_context):
    base_prompt = (
        "<|system|>You are DoctorGPT, a highly specialized medical AI assistant. "
        "Your role is to analyze patient medical records and provide detailed, personalized medical advice. "
        "You should communicate in a natural, conversational tone while maintaining professionalism. "
        "Avoid medical jargon unless necessary, and explain complex terms when used. "
        "Be empathetic and supportive in your responses. "
        "Base your advice strictly on the provided medical records and current medical knowledge. "
        "Always acknowledge the limitations of your analysis and recommend consulting a healthcare provider for definitive diagnosis and treatment.</s>\n"
        f"<|user|>Based on the patient's medical history, {question}</s>\n"
    )
    
    if pdf_context:
        base_prompt += f"<|context|>Patient's Medical History:\n{pdf_context}</s>\n"
    
    base_prompt += "<|assistant|>"
    return base_prompt

@app.route('/api/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.save(tmp_file.name)
            chunks = process_pdf(tmp_file.name)
            embeddings = get_embeddings(chunks)
            store_documents(chunks, embeddings)
        
        os.unlink(tmp_file.name)
        return jsonify({
            'message': f'Successfully processed and stored {len(chunks)} document chunks!',
            'chunks_count': len(chunks)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if len(question) > MAX_INPUT_LENGTH:
            return jsonify({'error': f'Question too long. Maximum length is {MAX_INPUT_LENGTH} characters'}), 400
        
        # Search for relevant document chunks
        pdf_context = None
        if client.count(COLLECTION_NAME).count > 0:
            relevant_texts = search_documents(question)
            pdf_context = "\n".join(relevant_texts)
        
        prompt = generate_prompt(question, pdf_context)
        
        inputs = tokenizer(prompt, return_tensors="pt", padding=True)
        input_ids = inputs["input_ids"].to(model.device)
        attention_mask = inputs["attention_mask"].to(model.device)
        
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pad_token_id=tokenizer.eos_token_id,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.split("<|assistant|>")[-1].strip()
        
        return jsonify({
            'response': response,
            'context': pdf_context
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
