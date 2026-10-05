import main

from fastapi.testclient import TestClient


client = TestClient(main.app)


def test_upload_rejects_unsupported_file_type():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "malicious.exe",
                b"fake executable content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only PDF and TXT files are allowed."
    )


def test_upload_rejects_file_over_5_mb():
    large_file = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.txt",
                large_file,
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "File is too large. Maximum size is 5 MB."
    )


def test_upload_strips_path_traversal(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "../../evil.txt",
                b"safe test content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "evil.txt"
    assert (tmp_path / "evil.txt").exists()
