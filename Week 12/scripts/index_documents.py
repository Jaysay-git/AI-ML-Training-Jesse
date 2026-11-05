from pathlib import Path
import sys

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.rag import ingest_documents


if __name__ == "__main__":
    try:
        print("Indexing shared project documents...")

        result = ingest_documents()

        print("\nShared document indexing completed.")
        print(f"Documents processed: {result['documents_processed']}")
        print(f"Chunks stored: {result['chunks_stored']}")
        print(f"Collection: {result['collection']}")

    except Exception as error:
        print(f"\nDocument indexing failed: {error}")
        raise