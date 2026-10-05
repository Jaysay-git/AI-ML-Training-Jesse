from pathlib import Path

from ingestion import extract_pdf_pages, extract_text


PDF_PATH = Path("uploads/Jesse Osifade - (Q2).pdf")


def test_extract_pdf_pages():
    pages = extract_pdf_pages(PDF_PATH)

    assert len(pages) == 3
    assert [page["page"] for page in pages] == [1, 2, 3]
    assert all(page["text"] for page in pages)


def test_extract_text_matches_pages():
    text = extract_text(PDF_PATH)
    pages = extract_pdf_pages(PDF_PATH)

    expected_text = "\n".join(
        page["text"]
        for page in pages
    )

    assert text == expected_text
