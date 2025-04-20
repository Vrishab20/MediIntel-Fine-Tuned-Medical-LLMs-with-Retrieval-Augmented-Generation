
# 🩺 MediIntel: Fine-Tuned Medical LLMs with Retrieval-Augmented Generation

**DoctorGPT** is a domain-specific AI assistant for medical document analysis. Built with a React frontend and a Flask backend, it leverages local embedding generation and a PEFT fine-tuned LLM to answer patient-related queries.

> 🧠 Live Demo: [https://mediintel.netlify.app](https://mediintel.netlify.app)  
> 🧪 Backend must be running locally for full functionality.

---

##  Overview

This AI assistant analyzes uploaded patient PDF records and answers personalized medical questions using:

- **Qdrant** for vector search
- **Ollama** for local embedding generation
- **PEFT fine-tuned Mistral 7B model** for response generation
- **React** (frontend) + **Flask** (backend)

---

##  Model Training & Fine-tuning

- The model was fine-tuned using the **HealthcareMagic 100K EN** dataset (`en.jsonl`) on medical Q&A.
- A **parameter-efficient fine-tuning (PEFT)** technique was applied to Mistral 7B using LoRA.
- The resulting model `Deanna/doctorgpt-ft` was created from this process.
- Base model: [`TheBloke/Mistral-7B-Instruct-v0.2-GPTQ`](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GPTQ)

---

## 🧰 Tech Stack

| Component     | Tech                    |
|---------------|-------------------------|
| Frontend      | React, Netlify          |
| Backend       | Flask, Transformers, Qdrant, Ollama |
| Embeddings    | `mxbai-embed-large` (via Ollama) |
| Vector Store  | Qdrant (local or cloud) |
| Model         | Mistral 7B + PEFT (GPTQ) |
| Storage       | Temp storage for PDFs   |

---

## 🌐 Hosting Details

- Frontend is hosted on **[Netlify](https://mediintel.netlify.app)**
- **Backend must be run locally** for now. The website interacts with `http://localhost:5000` APIs.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DoctorGPT.git
cd DoctorGPT
```

---

### 2. Install Backend Dependencies
Ensure you have Python 3.9+ and Ollama installed. Then:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

### 3. Setup Hugging Face Access
Make sure you have access to Mistral-7B-GPTQ and the Deanna model:

```bash
huggingface-cli login
# Enter your Hugging Face token
```

---

### 4. Run Backend Locally
```bash
python app.py
# Backend will start on http://localhost:5000
```

---

### 5. Run Frontend (Optional for Local Testing)
```bash
cd frontend
npm install
npm start
# Opens http://localhost:3000
```

---

## 📂 File Upload & Interaction Flow

1. Upload a medical PDF.
2. The backend:
   - Extracts text
   - Splits it into chunks
   - Embeds via Ollama
   - Stores it in Qdrant
3. Ask a medical question.
4. The backend retrieves relevant chunks and constructs a prompt.
5. Mistral 7B + PEFT generates a custom, context-aware response.

---

## 📸 Demo Response Screenshot

![DoctorGPT Screenshot](https://github.com/user-attachments/assets/c2be0766-5f79-47ef-a5ea-55f6a384acda)


---

## 🧾 License
This project is for educational and research purposes only. Not intended for actual medical use. Always consult a professional.

---

## 🙌 Acknowledgements

- [Hugging Face](https://huggingface.co)
- [Ollama](https://ollama.com)
- [Qdrant](https://qdrant.tech)
- [Healthcare Magic Dataset](https://huggingface.co/datasets/healthcare-magic)
- [TheBloke GPTQ Models](https://huggingface.co/TheBloke)
