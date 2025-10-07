from dotenv import load_dotenv
import os

load_dotenv()
print("EMBEDDING_MODEL:", os.getenv("EMBEDDING_MODEL"))
print("VECTOR_DB_PATH:", os.getenv("VECTOR_DB_PATH"))
print("SQLITE_DB_PATH:", os.getenv("SQLITE_DB_PATH"))