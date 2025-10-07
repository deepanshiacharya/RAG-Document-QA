import os
from db import init_db

if __name__ == "__main__":
    Session = init_db()
    print("SQLite database initialized at", os.getenv("SQLITE_DB_PATH"))