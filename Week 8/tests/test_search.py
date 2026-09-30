import main

from fastapi.testclient import TestClient


client = TestClient(main.app)


def test_search_rejects_empty_query():
    response = client.post(
        "/documents/search",
        params={"query": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Search query cannot be empty."


def test_search_rejects_invalid_n_results():
    response = client.post(
        "/documents/search",
        params={
            "query": "training",
            "n_results": 11,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "n_results must be between 1 and 10."
    )


def test_search_rejects_invalid_strategy():
    response = client.post(
        "/documents/search",
        params={
            "query": "training",
            "strategy": "invalid",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "strategy must be 'paragraph' or 'fixed'."
    )


def test_search_filters_by_paragraph_strategy(monkeypatch):
    def fake_embedding(text):
        return [0.0] * 3072

    def fake_query(**kwargs):
        assert kwargs["where"] == {
            "chunking_strategy": "paragraph"
        }

        return {
            "documents": [["Paragraph result"]],
            "metadatas": [[
                {
                    "filename": "Jesse Osifade - (Q2).pdf",
                    "chunk_index": 2,
                    "source": "uploads/Jesse Osifade - (Q2).pdf",
                    "chunking_strategy": "paragraph",
                    "pages": "2,3",
                }
            ]],
            "distances": [[0.52]],
        }

    monkeypatch.setattr(
        main,
        "generate_embedding",
        fake_embedding,
    )

    monkeypatch.setattr(
        main.collection,
        "query",
        fake_query,
    )

    response = client.post(
        "/documents/search",
        params={
            "query": "training and development",
            "strategy": "paragraph",
            "n_results": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "training and development"
    assert len(data["results"]) == 1
    assert data["results"][0]["chunking_strategy"] == "paragraph"
    assert data["results"][0]["pages"] == "2,3"
    assert data["results"][0]["distance"] == 0.52