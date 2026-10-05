from vector_store import collection


def test_vector_store_contains_expected_chunks():
    results = collection.get(
        limit=20,
        include=["documents", "metadatas"],
    )

    documents = results["documents"]
    metadatas = results["metadatas"]

    assert len(documents) == 11
    assert len(metadatas) == 11


def test_vector_store_contains_both_chunking_strategies():
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
    results = collection.get(
        limit=20,
        include=["metadatas"],
    )

    for metadata in results["metadatas"]:
        assert metadata["filename"] == "Jesse Osifade - (Q2).pdf"
        assert metadata["source"] == "uploads/Jesse Osifade - (Q2).pdf"
        assert metadata["chunking_strategy"] in {
            "paragraph",
            "fixed",
        }
        assert isinstance(metadata["chunk_index"], int)
        assert metadata["pages"]


def test_vector_store_has_expected_chunk_counts():
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
