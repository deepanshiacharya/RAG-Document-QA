from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
vector_db_path = Path(os.getenv("VECTOR_DB_PATH", "data/faiss_index"))
index_path = vector_db_path / "index.faiss"

# Ensure the directory exists
vector_db_path.mkdir(parents=True, exist_ok=True)

if index_path.exists():
    vectorstore = FAISS.load_local(str(vector_db_path), embeddings, allow_dangerous_deserialization=True)
    print(f"FAISS index loaded with {len(vectorstore.index_to_docstore_id)} chunks")
    for i, doc in enumerate(vectorstore.docstore._dict.values()):
        print(f"Chunk {i}: doc_id={doc.metadata.get('doc_id')}, filename={doc.metadata.get('filename')}, chunk_id={doc.metadata.get('chunk_id')}")
else:
    print("No FAISS index found. Please ingest documents first.")