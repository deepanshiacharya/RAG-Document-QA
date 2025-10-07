RAG Document Q&A App
A Dockerized Retrieval-Augmented Generation (RAG) application for document-based question answering using Streamlit and FastAPI.
Setup and Installation Instructions
Prerequisites

Docker Desktop (latest version)
Git
Python 3.12 (for local development, optional)

Local Installation

Clone the Repository :
git clone https://github.com/deepanshiacharya/RAG-Document-QA.git
cd RAG-Document-QA


Build the Docker Image
docker build -t rag-app .


Run the Container
docker run -p 8000:8000 -p 8501:8501 -p 11434:11434 rag-app


Access the App

Streamlit UI: http://localhost:8501
FastAPI Docs: http://localhost:8000/docs



Configuration Details for Using Different LLM Providers

Default Provider: Ollama with llama3:latest model (configured via ollama serve).
Custom LLM Providers:
Edit .env file (create if not present) with:OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_PROVIDER=ollama
MODEL_NAME=llama3:latest

For other providers (e.g., Hugging Face):
Install required packages in requirements.txt (e.g., transformers).
Update .env:LLM_PROVIDER=huggingface
HF_API_KEY=your_hf_api_key
MODEL_NAME=meta-llama/Llama-3-8B


Modify app/api.py to switch providers based on LLM_PROVIDER environment variable.


Uploading Rag_deepanshiAcharya.mp4…



