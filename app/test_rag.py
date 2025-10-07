from rag import RAGPipeline

if __name__ == "__main__":
    rag = RAGPipeline()
    question = "What is the main topic of the document?"  # Customize based on your test.pdf content
    result = rag.query(question)
    print("Question:", question)
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])