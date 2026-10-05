from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from vector_store import collection


def keyword_search(query: str, n_results: int = 10) -> list[dict]:
    """Search stored chunks using TF-IDF keyword similarity."""
    if not query.strip():
        return []

    stored = collection.get(
        include=["documents", "metadatas"]
    )

    documents = stored.get("documents", [])
    metadatas = stored.get("metadatas", [])
    ids = stored.get("ids", [])

    if not documents:
        return []

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
    )

    document_matrix = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        document_matrix,
    )[0]

    ranked_indices = scores.argsort()[::-1]

    results = []

    for index in ranked_indices[:n_results]:
        results.append(
            {
                "id": ids[index],
                "text": documents[index],
                "metadata": metadatas[index],
                "keyword_score": float(scores[index]),
            }
        )

    return results


def vector_search(query: str, n_results: int = 10) -> list[dict]:
    """Search stored chunks using vector similarity."""
    if not query.strip():
        return []

    from ingestion import generate_embedding

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    formatted = []

    for document, metadata, distance, source_id in zip(
        documents,
        metadatas,
        distances,
        ids,
    ):
        vector_score = 1 / (1 + float(distance))

        formatted.append(
            {
                "id": source_id,
                "text": document,
                "metadata": metadata,
                "vector_score": vector_score,
                "distance": float(distance),
            }
        )

    return formatted


def hybrid_search(
    query: str,
    n_results: int = 3,
) -> list[dict]:
    """Combine vector and keyword retrieval and rerank results."""
    if not query.strip():
        return []

    vector_results = vector_search(
        query,
        n_results=10,
    )

    keyword_results = keyword_search(
        query,
        n_results=10,
    )

    combined = {}

    for result in vector_results:
        combined[result["id"]] = {
            **result,
            "keyword_score": 0.0,
        }

    for result in keyword_results:
        if result["id"] in combined:
            combined[result["id"]]["keyword_score"] = (
                result["keyword_score"]
            )
        else:
            combined[result["id"]] = {
                **result,
                "vector_score": 0.0,
                "keyword_score": result["keyword_score"],
            }

    for result in combined.values():
        result["hybrid_score"] = (
            0.7 * result.get("vector_score", 0.0)
            + 0.3 * result.get("keyword_score", 0.0)
        )

    ranked = sorted(
        combined.values(),
        key=lambda result: result["hybrid_score"],
        reverse=True,
    )

    return ranked[:n_results]