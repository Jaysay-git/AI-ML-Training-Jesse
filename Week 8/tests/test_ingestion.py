from pathlib import Path

import pymupdf

from ingestion import extract_pdf_pages, extract_text


def create_test_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "test_document.pdf"

    document = pymupdf.open()

    pages = [
        "Page one test content.\n\nDepartment: Information Technology.",
        "Page two test content.\n\nTraining and development information.",
        "Page three test content.\n\nAdditional project information.",
    ]

    for text in pages:
        page = document.new_page()
        page.insert_text((72, 72), text)

    document.save(pdf_path)
    document.close()

    return pdf_path


def test_extract_pdf_pages(tmp_path):
    pdf_path = create_test_pdf(tmp_path)

    pages = extract_pdf_pages(pdf_path)

    assert len(pages) == 3
    assert [page["page"] for page in pages] == [1, 2, 3]
    assert all(page["text"] for page in pages)


def test_extract_text_matches_pages(tmp_path):
    pdf_path = create_test_pdf(tmp_path)

    text = extract_text(pdf_path)
    pages = extract_pdf_pages(pdf_path)

    expected_text = "\n".join(
        page["text"]
        for page in pages
    )

    assert text == expected_text