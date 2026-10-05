import uuid

import chromadb


def create_test_collection():
    client = chromadb.EphemeralClient()

    collection = client.create_collection(
        name=f"test_documents_{uuid.uuid4().hex}"
    )

    chunks = [
        "Paragraph chunk one.",
        "Paragraph chunk two.",
        "Paragraph chunk three.",
        "Paragraph chunk four.",
        "Fixed chunk one.",
        "Fixed chunk two.",
        "Fixed chunk three.",
        "Fixed chunk four.",
        "Fixed chunk five.",
        "Fixed chunk six.",
        "Fixed chunk seven.",
    ]

    strategies = (
        ["paragraph"] * 4
        + ["fixed"] * 7
    )

    metadatas = [
        {
            "filename": "test_document.pdf",
            "chunk_index": index,
            "source": "uploads/test_document.pdf",
            "chunking_strategy": strategy,
            "pages": "1",
        }
        for index, strategy in enumerate(strategies)
    ]

    embeddings = [
        [0.0] * 3072
        for _ in chunks
    ]

    collection.add(
        ids=[
            f"test_document.pdf-{strategy}-{index}"
            for index, strategy in enumerate(strategies)
        ],
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return collection


def test_vector_store_contains_expected_chunks():
    collection = create_test_collection()

    results = collection.get(
        limit=20,
        include=["documents", "metadatas"],
    )

    documents = results["documents"]
    metadatas = results["metadatas"]

    assert len(documents) == 11
    assert len(metadatas) == 11


def test_vector_store_contains_both_chunking_strategies():
    collection = create_test_collection()

    results = collection.get(
        limit=20,
        include=["metadatas"],
    )

    strategies = {
        metadata["chunking_strategy"]
        for metadata in results["metadatas"]
    }

    assert strategies == {"paragraph", "fixed"}


def test_vector_store_metadata_contains_source_and_pages():
    collection = create_test_collection()

    results = collection.get(
        limit=20,
        include=["metadatas"],
    )

    for metadata in results["metadatas"]:
        assert metadata["filename"] == "test_document.pdf"
        assert metadata["source"] == "uploads/test_document.pdf"
        assert metadata["chunking_strategy"] in {
            "paragraph",
            "fixed",
        }
        assert isinstance(metadata["chunk_index"], int)
        assert metadata["pages"]


def test_vector_store_has_expected_chunk_counts():
    collection = create_test_collection()

    results = collection.get(
        limit=20,
        include=["metadatas"],
    )

    strategies = [
        metadata["chunking_strategy"]
        for metadata in results["metadatas"]
    ]

    assert strategies.count("paragraph") == 4
    assert strategies.count("fixed") == 7