from db import init_db, Document
from sqlalchemy import text

if __name__ == "__main__":
    Session = init_db()
    session = Session()
    result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("Tables:", result)
    docs = session.query(Document).all()
    for doc in docs:
        print(f"Doc ID: {doc.id}, Filename: {doc.filename}, Pages: {doc.page_count}, Chunks: {doc.chunk_count}")
    session.close()