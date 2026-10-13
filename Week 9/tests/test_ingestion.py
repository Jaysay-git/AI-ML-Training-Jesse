import pymupdf

from ingestion import extract_pdf_pages, extract_text


def create_test_pdf(file_path):
    """Create a synthetic three-page PDF for testing."""
    document = pymupdf.open()

    for page_number in range(1, 4):
        page = document.new_page()
        page.insert_text(
            (72, 72),
            f"Test page {page_number} contains sample text.",
        )

    document.save(file_path)
    document.close()


def test_extract_pdf_pages(tmp_path):
    pdf_path = tmp_path / "synthetic.pdf"
    create_test_pdf(pdf_path)

    pages = extract_pdf_pages(pdf_path)

    assert len(pages) == 3
    assert [page["page"] for page in pages] == [1, 2, 3]
    assert all(page["text"] for page in pages)


def test_extract_text_matches_pages(tmp_path):
    pdf_path = tmp_path / "synthetic.pdf"
    create_test_pdf(pdf_path)

    text = extract_text(pdf_path)
    pages = extract_pdf_pages(pdf_path)

    expected_text = "\n".join(
        page["text"] for page in pages
    )

    assert text == expected_text