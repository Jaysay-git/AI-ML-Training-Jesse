from ingestion import generate_embedding
from vector_store import collection


query = "What training and development does the employee want in the next quarter?"

query_embedding = generate_embedding(query)


for strategy in ["paragraph", "fixed"]:
    print(f"\n{'=' * 60}")
    print(f"Strategy: {strategy}")
    print(f"{'=' * 60}")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2,
        where={"chunking_strategy": strategy},
    )

    for index, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ),
        start=1,
    ):
        print(f"\n--- Result {index} ---")
        print(f"Distance: {distance}")
        print(f"Chunk index: {metadata['chunk_index']}")
        print(f"Text: {document[:500]}")