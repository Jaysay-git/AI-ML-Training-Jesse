
import uuid

import chromadb
import pytest


@pytest.fixture
def seeded_collection(monkeypatch):
    """Create an isolated Chroma collection for retrieval tests."""
    import ingestion
    import retrieval
    import vector_store

    client = chromadb.EphemeralClient()
    test_collection = client.create_collection(
        name=f"week9_test_{uuid.uuid4().hex}"
    )

    monkeypatch.setattr(
        vector_store, "collection", test_collection
    )
    monkeypatch.setattr(
        retrieval, "collection", test_collection
    )
    monkeypatch.setattr(
        ingestion,
        "generate_embedding",
        lambda text: [1.0, 0.0, 0.0],
    )

    paragraph_chunks = [
        (
            "The employee works in the Information Technology "
            "department as a Junior Product Designer."
        ),
        "The synthetic document describes project planning.",
        "The synthetic document describes design collaboration.",
        "The synthetic document describes product delivery.",
    ]

    fixed_chunks = [
        f"Synthetic fixed-size document section number {number}."
        for number in range(1, 8)
    ]

    vector_store.add_chunks(
        chunks=paragraph_chunks,
        embeddings=[[1.0, 0.0, 0.0]] * len(paragraph_chunks),
        filename="test-document.pdf",
        strategy="paragraph",
        pages=[[1], [1], [2], [3]],
    )

    vector_store.add_chunks(
        chunks=fixed_chunks,
        embeddings=[[1.0, 0.0, 0.0]] * len(fixed_chunks),
        filename="test-document.pdf",
        strategy="fixed",
        pages=[[1], [1], [2], [2], [2], [3], [3]],
    )

    return test_collection
