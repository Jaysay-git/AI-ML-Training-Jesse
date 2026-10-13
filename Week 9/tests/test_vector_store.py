def test_vector_store_contains_expected_chunks(seeded_collection):
    results = seeded_collection.get(
        limit=20,
        include=["documents", "metadatas"],
    )

    assert len(results["documents"]) == 11
    assert len(results["metadatas"]) == 11


def test_vector_store_contains_both_chunking_strategies(
    seeded_collection,
):
    results = seeded_collection.get(
        limit=20,
        include=["metadatas"],
    )

    strategies = {
        metadata["chunking_strategy"]
        for metadata in results["metadatas"]
    }

    assert strategies == {"paragraph", "fixed"}


def test_vector_store_metadata_contains_source_and_pages(
    seeded_collection,
):
    results = seeded_collection.get(
        limit=20,
        include=["metadatas"],
    )

    for metadata in results["metadatas"]:
        assert metadata["filename"] == "test-document.pdf"
        assert metadata["source"] == "uploads/test-document.pdf"
        assert metadata["chunking_strategy"] in {
            "paragraph",
            "fixed",
        }
        assert isinstance(metadata["chunk_index"], int)
        assert metadata["pages"]


def test_vector_store_has_expected_chunk_counts(seeded_collection):
    results = seeded_collection.get(
        limit=20,
        include=["metadatas"],
    )

    strategies = [
        metadata["chunking_strategy"]
        for metadata in results["metadatas"]
    ]

    assert strategies.count("paragraph") == 4
    assert strategies.count("fixed") == 7