from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from app.ingestion import DocumentIngestion
from app.rag import RAGPipeline
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

rag_pipeline = RAGPipeline()

def get_ingestion():
    return DocumentIngestion()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        ingestion = get_ingestion()
        doc_id = ingestion.ingest_document(file, file.filename)
        return JSONResponse({"message": "File uploaded successfully", "doc_id": doc_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query")
async def query_document(question: str):  # Remove Form(...) to accept JSON
    print(f"Debug: Received request with question: {question}")
    try:
        response = rag_pipeline.query(question)
        return JSONResponse(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    ingestion = get_ingestion()
    docs = ingestion.session.query(Document).all()
    return [{"doc_id": doc.id, "filename": doc.filename, "page_count": doc.page_count, "chunk_count": doc.chunk_count, "upload_time": doc.upload_time.isoformat()} for doc in docs]