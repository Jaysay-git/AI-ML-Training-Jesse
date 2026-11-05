from uuid import uuid4

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import SessionLocal
from app.database.models import User
from sqlalchemy import select


client = TestClient(app)


@pytest.fixture(scope="module")
def document_user():
    email = f"document-user-{uuid4().hex}@example.com"
    password = "DocumentTest123!"

    signup = client.post(
        "/auth/signup",
        json={"email": email, "password": password},
    )
    assert signup.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    yield {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": signup.json()["id"],
    }

    db = SessionLocal()
    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_document_upload_requires_authentication():
    response = client.post(
        "/documents/upload",
        files={"file": ("test.txt", b"Private test document", "text/plain")},
    )

    assert response.status_code == 401


def test_txt_upload_succeeds_and_uses_current_user(
    document_user,
    monkeypatch,
):
    captured = {}

    def fake_ingest(text, filename, user_id):
        captured.update({
            "text": text,
            "filename": filename,
            "user_id": user_id,
        })
        return {
            "document_id": "test_document_123",
            "filename": filename,
            "chunks_stored": 2,
        }

    monkeypatch.setattr(
        "app.api.documents.ingest_uploaded_document",
        fake_ingest,
    )

    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": (
                "private.txt",
                b"Golden Cassava costs 7250 naira in Enugu.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["chunks_stored"] == 2
    assert captured["user_id"] == document_user["user_id"]
    assert captured["filename"] == "private.txt"
    assert "Golden Cassava" in captured["text"]


def test_pdf_upload_extracts_text(
    document_user,
    monkeypatch,
):
    captured = {}

    def fake_ingest(text, filename, user_id):
        captured["text"] = text
        captured["user_id"] = user_id
        return {
            "document_id": "test_pdf_123",
            "filename": filename,
            "chunks_stored": 1,
        }

    monkeypatch.setattr(
        "app.api.documents.ingest_uploaded_document",
        fake_ingest,
    )

    pdf = pymupdf.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "PDF document extraction test.")
    pdf_bytes = pdf.tobytes()
    pdf.close()

    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": (
                "test.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert "PDF document extraction test." in captured["text"]
    assert captured["user_id"] == document_user["user_id"]


def test_unsupported_file_type_is_rejected(document_user):
    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": (
                "prices.csv",
                b"commodity,price",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert "Only PDF and TXT" in response.json()["detail"]


def test_empty_file_is_rejected(document_user):
    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": ("empty.txt", b"", "text/plain"),
        },
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_invalid_utf8_txt_is_rejected(document_user):
    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfa",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "UTF-8" in response.json()["detail"]


def test_file_over_5mb_is_rejected(document_user):
    oversized_content = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": (
                "oversized.txt",
                oversized_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 413


def test_indexing_failure_returns_service_unavailable(
    document_user,
    monkeypatch,
):
    def failing_ingest(**kwargs):
        raise RuntimeError("Embedding service unavailable")

    monkeypatch.setattr(
        "app.api.documents.ingest_uploaded_document",
        failing_ingest,
    )

    response = client.post(
        "/documents/upload",
        headers=document_user["headers"],
        files={
            "file": (
                "failure.txt",
                b"This document should fail indexing.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 503
    assert "indexing is temporarily unavailable" in (
        response.json()["detail"]
    ).lower()


@pytest.mark.parametrize("user_id", [101, 202])
def test_document_retrieval_filter_is_user_scoped(
    user_id,
    monkeypatch,
):
    from app.agent import rag

    captured = {}

    class FakeCollection:
        def count(self):
            return 2

        def query(self, **kwargs):
            captured.update(kwargs)
            return {
                "documents": [["Private test passage"]],
                "metadatas": [[{
                    "source": "private.txt",
                    "owner_id": str(user_id),
                }]],
                "distances": [[0.1]],
            }

    monkeypatch.setattr(
        rag,
        "get_collection",
        lambda: FakeCollection(),
    )
    monkeypatch.setattr(
        rag,
        "create_embedding",
        lambda text, task_type: [0.1, 0.2],
    )

    result = rag.ask_documents(
        "What is in my document?",
        user_id=user_id,
    )

    assert result["found"] is True
    assert captured["where"] == {
        "$or": [
            {"owner_id": "shared"},
            {"owner_id": str(user_id)},
        ]
    }
