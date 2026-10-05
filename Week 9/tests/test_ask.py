from fastapi.testclient import TestClient

from main import app
from schemas import GroundedAnswer


client = TestClient(app)


def test_ask_returns_cited_answer(monkeypatch):
    def mock_hybrid_search(question, n_results):
        return [
            {
                "id": "source-1",
                "text": "The employee wants AI training.",
                "metadata": {
                    "filename": "test.pdf",
                    "pages": "2",
                    "chunk_index": 1,
                },
            },
            {
                "id": "source-2",
                "text": "The employee wants another certification.",
                "metadata": {
                    "filename": "test.pdf",
                    "pages": "3",
                    "chunk_index": 2,
                },
            },
        ]

    def mock_generate_grounded_answer(question, sources):
        return GroundedAnswer(
            answer="The employee wants AI training [S1] and another certification [S2].",
            citations=["S1", "S2"],
        )

    monkeypatch.setattr(
        "main.hybrid_search",
        mock_hybrid_search,
    )

    monkeypatch.setattr(
        "main.generate_grounded_answer",
        mock_generate_grounded_answer,
    )

    response = client.post(
        "/ask",
        json={
            "question": "What training does the employee want?",
            "n_results": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What training does the employee want?"
    assert "AI training" in data["answer"]
    assert len(data["citations"]) == 2

    assert data["citations"][0]["source_id"] == "S1"
    assert data["citations"][0]["filename"] == "test.pdf"
    assert data["citations"][0]["pages"] == "2"
    assert data["citations"][0]["chunk_index"] == 1


def test_ask_refuses_when_no_valid_citations(monkeypatch):
    def mock_hybrid_search(question, n_results):
        return [
            {
                "id": "source-1",
                "text": "Some document text.",
                "metadata": {
                    "filename": "test.pdf",
                    "pages": "1",
                    "chunk_index": 0,
                },
            }
        ]

    def mock_generate_grounded_answer(question, sources):
        return GroundedAnswer(
            answer="This is an unsupported answer.",
            citations=["S99"],
        )

    monkeypatch.setattr(
        "main.hybrid_search",
        mock_hybrid_search,
    )

    monkeypatch.setattr(
        "main.generate_grounded_answer",
        mock_generate_grounded_answer,
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is something?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["citations"] == []
    assert "not enough information" in data["answer"].lower()


def test_ask_rejects_empty_question():
    response = client.post(
        "/ask",
        json={
            "question": "   ",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."