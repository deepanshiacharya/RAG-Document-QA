from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    chunk_count = Column(Integer, default=0)

def init_db():
    db_path = os.getenv("SQLITE_DB_PATH")
    if not db_path:
        raise ValueError("SQLITE_DB_PATH not set in .env")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

def add_document(session, filename, filepath, page_count):
    doc = Document(filename=filename, filepath=filepath, page_count=page_count)
    session.add(doc)
    session.commit()
    return doc.id

def get_document(session, doc_id):
    return session.query(Document).filter(Document.id == doc_id).first()

def get_all_documents(session):
    return session.query(Document).all()

def update_chunk_count(session, doc_id, chunk_count):
    doc = session.query(Document).filter(Document.id == doc_id).first()
    if doc:
        doc.chunk_count = chunk_count
        session.commit()