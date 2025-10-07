import os
import uuid
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
import docx2txt
from app.db import init_db, add_document, update_chunk_count, Document
from dotenv import load_dotenv
from fastapi import UploadFile
import shutil

load_dotenv()

class DocumentIngestion:
    def __init__(self):
        self.max_docs = int(os.getenv("MAX_DOCS", 20))
        self.max_pages = int(os.getenv("MAX_PAGES_PER_DOC", 1000))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
        self.embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
        self.vector_db_path = os.getenv("VECTOR_DB_PATH")
        self.session_factory = init_db()
        self.session = self.session_factory()
        self.vectorstore = None
        if os.path.exists(self.vector_db_path):
            try:
                self.vectorstore = FAISS.load_local(self.vector_db_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception:
                self.vectorstore = None

    def __del__(self):
        if hasattr(self, 'session') and self.session is not None:
            self.session.close()

    def count_documents(self):
        return len(self.session.query(Document).all())

    def validate_document(self, file_path):
        if self.count_documents() >= self.max_docs:
            raise ValueError(f"Maximum document limit ({self.max_docs}) reached.")
        # For UploadFile, use filename from the object
        if hasattr(file_path, 'filename'):
            filename = file_path.filename
            if not (filename.endswith(".pdf") or filename.endswith(".docx")):
                raise ValueError("Unsupported file type. Use PDF or DOCX.")
            if filename.endswith(".pdf"):
                reader = PdfReader(file_path.file)
                page_count = len(reader.pages)
                if page_count > self.max_pages:
                    raise ValueError(f"Document exceeds page limit ({self.max_pages}).")
                return page_count
            elif filename.endswith(".docx"):
                return 1
        else:
            if not (file_path.endswith(".pdf") or file_path.endswith(".docx")):
                raise ValueError("Unsupported file type. Use PDF or DOCX.")
            if file_path.endswith(".pdf"):
                reader = PdfReader(file_path)
                page_count = len(reader.pages)
                if page_count > self.max_pages:
                    raise ValueError(f"Document exceeds page limit ({self.max_pages}).")
                return page_count
            elif file_path.endswith(".docx"):
                return 1
        raise ValueError("Invalid file format")

    def extract_text(self, file_path):
        if hasattr(file_path, 'file'):
            if file_path.filename.endswith(".pdf"):
                reader = PdfReader(file_path.file)
                return "".join(page.extract_text() or "" for page in reader.pages)
            elif file_path.filename.endswith(".docx"):
                return docx2txt.process(file_path.file)
        else:
            if file_path.endswith(".pdf"):
                reader = PdfReader(file_path)
                return "".join(page.extract_text() or "" for page in reader.pages)
            elif file_path.endswith(".docx"):
                return docx2txt.process(file_path)
        return ""

    def ingest_document(self, file: UploadFile, filename: str):
        page_count = self.validate_document(file)
        # Save the uploaded file to a temporary location
        save_path = Path("data") / f"{uuid.uuid4()}_{filename}"
        save_path.parent.mkdir(exist_ok=True)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Add to SQLite
        doc_id = add_document(self.session, filename, str(save_path), page_count)
        # Extract and chunk
        text = self.extract_text(file)
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = splitter.split_text(text)
        metadata = [{"doc_id": doc_id, "chunk_id": i, "filename": filename} for i in range(len(chunks))]
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_texts(chunks, self.embeddings, metadatas=metadata)
        else:
            self.vectorstore.add_texts(chunks, metadatas=metadata)
        self.vectorstore.save_local(self.vector_db_path)
        update_chunk_count(self.session, doc_id, len(chunks))
        self.session.commit()
        return doc_id