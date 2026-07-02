#backend/app/main.py
import os
from backend.app.index.indexer import Indexer
from dotenv import load_dotenv

load_dotenv()

DATA = os.environ.get("DATA", "data")

if __name__ == "__main__":
    indexer = Indexer()

    indexer.index_directory(str(DATA))

    print(f"Indexed {len(indexer.documents)} documents.")
    print(f"Vocabulary size: {indexer.index.vocabulary_size()}.")