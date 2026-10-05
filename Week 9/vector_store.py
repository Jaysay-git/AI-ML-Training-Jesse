import chromadb


client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def add_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
    strategy: str,
    pages: list[list[int]] | None = None,
) -> None:
    """Store document chunks, embeddings, and metadata in Chroma."""

    if pages is None:
        pages = [[] for _ in chunks]

    if len(pages) != len(chunks):
        raise ValueError("pages must contain one entry per chunk.")

    ids = [
        f"{filename}-{strategy}-{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "filename": filename,
            "chunk_index": index,
            "source": f"uploads/{filename}",
            "chunking_strategy": strategy,
            "pages": ",".join(
                str(page) for page in pages[index]
            ),
        }
        for index in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
