# Fine-Tuned Medical LLM with Retrieval-Augmented Generation

**DoctorGPT** is a domain-specific AI assistant for medical document analysis. Built with a React frontend and a Flask backend, it leverages local embedding generation and a PEFT fine-tuned LLM to answer patient-related queries.

>  Live Demo: [https://mediintel.netlify.app](https://mediintel.netlify.app)  
>  Backend must be running locally for full functionality.

---

##  Overview

This AI assistant analyzes uploaded patient PDF records and answers personalized medical questions using:

- **Qdrant** for vector search  
- **Ollama** for local embedding generation  
- **PEFT fine-tuned Mistral 7B model** for response generation  
- **React** (frontend) + **Flask** (backend)

---

##  Model Training & Fine-tuning

- The model was fine-tuned on the **HealthcareMagic 100K EN** dataset (`en.jsonl`) comprising medical Q&A conversations.
- A **parameter-efficient fine-tuning (PEFT)** technique was applied using LoRA on top of the **Mistral 7B** architecture.
- The resulting fine-tuned model is available at:  
  🔗 [Deanna/doctorgpt-ft on Hugging Face](https://huggingface.co/Deanna/doctorgpt-ft/tree/main)
- Base model: [`TheBloke/Mistral-7B-Instruct-v0.2-GPTQ`](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GPTQ)

---

##  Tech Stack

| Component     | Tech                                      |
|---------------|-------------------------------------------|
| Frontend      | React, Netlify                            |
| Backend       | Flask, Transformers, Qdrant, Ollama       |
| Embeddings    | `mxbai-embed-large` via Ollama            |
| Vector Store  | Qdrant (local or cloud)                   |
| Model         | Mistral 7B + PEFT (GPTQ)                  |
| Storage       | Temp local file storage for PDFs          |

---

## 🌐 Hosting Details

- Frontend is hosted on **[Netlify](https://mediintel.netlify.app)**  
- **Backend must be run locally** and interacts via `http://localhost:5000` APIs

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DoctorGPT.git
cd DoctorGPT
```

### 2. Install Backend Dependencies
Ensure Python 3.9+ and Ollama are installed:
```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Hugging Face Access
```bash
huggingface-cli login
# Enter your Hugging Face token when prompted
```

### 4. Run Backend Locally
```bash
python app.py
# Starts backend at http://localhost:5000
```

### 5. Run Frontend
```bash
cd frontend
npm install
npm start
# Opens http://localhost:3000
```

---

## 📂 File Upload & Query Flow

1. Upload a medical PDF.
2. Backend extracts text → splits into chunks → embeds using Ollama → stores in Qdrant.
3. User enters a medical question.
4. Backend retrieves relevant chunks and constructs a prompt.
5. Mistral 7B + PEFT generates a medically coherent, context-aware response.

---

##  Demo Screenshot

![DoctorGPT Screenshot](https://github.com/user-attachments/assets/c2be0766-5f79-47ef-a5ea-55f6a384acda)

---

##  License

For educational and research use only. Not intended for clinical decision-making.

---

##  Acknowledgements

- [Hugging Face](https://huggingface.co)  
- [Ollama](https://ollama.com)  
- [Qdrant](https://qdrant.tech)  
- [Healthcare Magic Dataset](https://huggingface.co/datasets/healthcare-magic)  
- [TheBloke GPTQ Models](https://huggingface.co/TheBloke)
