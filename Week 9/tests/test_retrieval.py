from retrieval import keyword_search, vector_search, hybrid_search


def test_keyword_search_returns_results():
    results = keyword_search(
        "What department and position does the employee have?",
        n_results=3,
    )

    assert results
    assert len(results) <= 3
    assert all("id" in result for result in results)
    assert all("text" in result for result in results)
    assert all("metadata" in result for result in results)
    assert all("keyword_score" in result for result in results)


def test_vector_search_returns_results():
    results = vector_search(
        "What department and position does the employee have?",
        n_results=3,
    )

    assert results
    assert len(results) <= 3
    assert all("id" in result for result in results)
    assert all("vector_score" in result for result in results)
    assert all("distance" in result for result in results)


def test_hybrid_search_returns_ranked_results():
    results = hybrid_search(
        "What department and position does the employee have?",
        n_results=3,
    )

    assert results
    assert len(results) <= 3
    assert all("id" in result for result in results)
    assert all("hybrid_score" in result for result in results)

    scores = [result["hybrid_score"] for result in results]

    assert scores == sorted(scores, reverse=True)


def test_empty_queries_return_no_results():
    assert keyword_search("") == []
    assert vector_search("") == []
    assert hybrid_search("") == []