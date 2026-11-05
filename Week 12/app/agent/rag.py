import os
import uuid
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "naija_cost_documents"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

_client = None
_collection = None


def get_gemini_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        _client = genai.Client(api_key=api_key)

    return _client


def get_collection():
    global _collection

    if _collection is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))

        _collection = chroma.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    return _collection


def create_embedding(text: str, task_type: str):
    response = get_gemini_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    return response.embeddings[0].values


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120):
    text = " ".join(text.split())
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def store_document(
    text: str,
    filename: str,
    owner_id: str,
    document_id: str,
):
    """Chunk, embed and store a document with ownership metadata."""

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("The document contains no readable text.")

    collection = get_collection()

    ids = []
    metadatas = []
    embeddings = []

    for index, chunk in enumerate(chunks):
        ids.append(f"{document_id}_{index}")

        metadatas.append({
            "source": filename,
            "owner_id": owner_id,
            "document_id": document_id,
            "chunk_index": index,
        })

        embeddings.append(
            create_embedding(chunk, "RETRIEVAL_DOCUMENT")
        )

    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_stored": len(chunks),
    }


def ingest_documents():
    """Index project Markdown documents as shared documentation."""

    files = list(DOCUMENTS_DIR.glob("*.md"))

    if not files:
        raise FileNotFoundError(
            f"No Markdown documents found in {DOCUMENTS_DIR}"
        )

    results = []
    total_chunks = 0

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")

        document_id = f"shared_{file_path.stem}"

        result = store_document(
            text=content,
            filename=file_path.name,
            owner_id="shared",
            document_id=document_id,
        )

        results.append(result)
        total_chunks += result["chunks_stored"]

    return {
        "status": "success",
        "documents_processed": len(results),
        "chunks_stored": total_chunks,
        "collection": COLLECTION_NAME,
    }


def ingest_uploaded_document(
    text: str,
    filename: str,
    user_id: int,
):
    """Index a PDF or TXT document for its uploading user only."""

    document_id = f"user_{user_id}_{uuid.uuid4().hex}"

    return store_document(
        text=text,
        filename=filename,
        owner_id=str(user_id),
        document_id=document_id,
    )


def ask_documents(
    question: str,
    user_id: int | None = None,
    top_k: int = 3,
):
    """
    Retrieve shared project documentation and, when authenticated,
    documents uploaded by the current user.
    """

    collection = get_collection()

    if user_id is None:
        access_filter = {"owner_id": "shared"}
    else:
        access_filter = {
            "$or": [
                {"owner_id": "shared"},
                {"owner_id": str(user_id)},
            ]
        }

    matching_count = collection.count()

    if matching_count == 0:
        return {
            "found": False,
            "message": "No accessible documents have been indexed yet.",
            "sources": [],
        }

    query_embedding = create_embedding(
        question,
        "RETRIEVAL_QUERY",
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, matching_count),
        where=access_filter,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    sources = []

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]

        sources.append({
            "citation": f"[D{index + 1}]",
            "source": metadata["source"],
            "content": document,
            "distance": round(
                results["distances"][0][index],
                4,
            ),
        })

    context = "\n\n".join(
        f'{item["citation"]} Source: {item["source"]}\n'
        f'{item["content"]}'
        for item in sources
    )

    return {
        "found": bool(sources),
        "question": question,
        "context": context,
        "sources": sources,
        "message": (
            "Relevant document passages retrieved."
            if sources
            else "No relevant document passages found."
        ),
    }
