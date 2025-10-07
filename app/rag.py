import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
        self.vector_db_path = os.getenv("VECTOR_DB_PATH")
        self.vectorstore = None  # Initialize as None, load on demand
        self.llm_model = os.getenv("LLM_MODEL", "llama3:latest")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model=self.llm_model,
            base_url=self.ollama_base_url,
            temperature=0.2
        )

    def _load_vectorstore(self):
        if self.vectorstore is None and os.path.exists(self.vector_db_path):
            self.vectorstore = FAISS.load_local(
                self.vector_db_path, self.embeddings, allow_dangerous_deserialization=True
            )
        elif self.vectorstore is None:
            # Create an empty vectorstore if no index exists
            self.vectorstore = FAISS.from_texts([], self.embeddings)
        return self.vectorstore

    def query(self, question, top_k=5):
        # Load or initialize vectorstore on demand
        vectorstore = self._load_vectorstore()
        # Retrieve relevant chunks
        results = vectorstore.similarity_search(question, k=top_k)
        if not results:
            return {"answer": "No relevant information found in uploaded documents.", "sources": []}
        
        # Prepare context
        context = "\n\n".join([doc.page_content for doc in results])
        sources = [
            {"doc_id": doc.metadata.get("doc_id"), "filename": doc.metadata.get("filename"), "chunk_id": doc.metadata.get("chunk_id")}
            for doc in results
        ]

        # Craft prompt for Llama 3
        prompt = f"""You are a helpful assistant. Answer the following question based ONLY on the provided context. 
Keep your response concise, accurate, and relevant. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {question}

Answer:"""

        # Generate response with Ollama
        try:
            answer = self.llm.invoke(prompt)
        except Exception as e:
            answer = f"Error generating response: {str(e)} (Ensure Ollama is running with {self.llm_model})"

        return {"answer": answer.strip(), "sources": sources}