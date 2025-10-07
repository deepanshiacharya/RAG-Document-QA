from ingestion import DocumentIngestion

if __name__ == "__main__":
    ingestion = DocumentIngestion()
    doc_id = ingestion.ingest_document("test.pdf", "test.pdf")
    print(f"Document ingested with ID: {doc_id}")