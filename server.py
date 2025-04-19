from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import tempfile
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import ollama
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Constants
MAX_INPUT_LENGTH = 1000
MAX_NEW_TOKENS = 280
COLLECTION_NAME = "medical_docs"
VECTOR_SIZE = 1024  # mxbai-embed-large vector size
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mxbai-embed-large:335m")

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def ensure_ollama_model():
    """Ensure the Ollama model is available locally"""
    try:
        ollama.show(OLLAMA_MODEL)
    except Exception:
        try:
            ollama.pull(OLLAMA_MODEL)
        except Exception as e:
            raise Exception(f"Failed to pull model: {str(e)}")

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
        raise Exception(f"Failed to get embeddings: {str(e)}")

def process_pdf(pdf_file):
    """Process PDF file and extract text"""
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
    """Store documents in Qdrant"""
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
    """Search documents in Qdrant"""
    query_embedding = get_embeddings([query])[0]
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )
    relevant_texts = [hit.payload["text"] for hit in search_result]
    return relevant_texts

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    question = request.form.get('question', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.save(tmp_file.name)
            
            # Process PDF
            chunks = process_pdf(tmp_file.name)
            
            # Get embeddings
            embeddings = get_embeddings(chunks)
            
            # Store documents
            store_documents(chunks, embeddings)
            
            # Search for relevant documents
            relevant_texts = search_documents(question)
            
            # Generate response using Ollama
            context = "\n".join(relevant_texts)
            prompt = f"Based on the following medical information:\n\n{context}\n\nQuestion: {question}\n\nAnswer:"
            
            response = ollama.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                stream=False
            )
            
            return jsonify({'response': response['response']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary file
        if 'tmp_file' in locals():
            os.unlink(tmp_file.name)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 