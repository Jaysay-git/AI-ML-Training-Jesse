from ingestion import chunk_text, chunk_text_by_paragraph


def test_fixed_chunking_returns_chunks():
    text = "A" * 1200

    chunks = chunk_text(
        text,
        chunk_size=500,
        overlap=50,
    )

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)


def test_fixed_chunking_has_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 50

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1
    assert chunks[0][-20:] == chunks[1][:20]


def test_fixed_chunking_empty_text():
    assert chunk_text("") == []


def test_paragraph_chunking_preserves_paragraphs():
    text = (
        "First paragraph with useful information.\n\n"
        "Second paragraph with more information.\n\n"
        "Third paragraph with additional information."
    )

    chunks = chunk_text_by_paragraph(
        text,
        max_chars=1000,
    )

    assert len(chunks) == 1
    assert "First paragraph" in chunks[0]
    assert "Second paragraph" in chunks[0]
    assert "Third paragraph" in chunks[0]


def test_paragraph_chunking_empty_text():
    assert chunk_text_by_paragraph("") == []