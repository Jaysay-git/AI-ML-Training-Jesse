from pathlib import Path

import pymupdf
from dotenv import load_dotenv
from google import genai

from vector_store import add_chunks


load_dotenv()

def get_gemini_client():
    """Create the Gemini client only when it is needed."""
    return genai.Client()


def extract_text(file_path: Path) -> str:
    """Extract text from a PDF or TXT document."""
    extension = file_path.suffix.lower()

    if extension == ".txt":
        return file_path.read_text(encoding="utf-8")

    if extension == ".pdf":
        pages = extract_pdf_pages(file_path)
        return "\n".join(
            page["text"]
            for page in pages
        )

    raise ValueError("Unsupported file type.")


def extract_pdf_pages(file_path: Path) -> list[dict]:
    """Extract PDF text while preserving page numbers."""

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Page-aware extraction is only supported for PDF files."
        )

    pages = []

    with pymupdf.open(file_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text().strip()

            if text:
                pages.append(
                    {
                        "page": page_number,
                        "text": text,
                    }
                )

    return pages


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split text into fixed-size overlapping chunks."""

    if not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def chunk_text_by_paragraph(
    text: str,
    max_chars: int = 1000,
) -> list[str]:
    """Split text using paragraph boundaries with a maximum size."""

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if len(paragraph) > max_chars:

            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            for start in range(0, len(paragraph), max_chars):
                chunks.append(
                    paragraph[start:start + max_chars].strip()
                )

        elif not current_chunk:

            current_chunk = paragraph

        elif len(current_chunk) + len(paragraph) + 2 <= max_chars:

            current_chunk += "\n\n" + paragraph

        else:

            chunks.append(current_chunk)
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def generate_embedding(text: str) -> list[float]:
    """Generate a Gemini embedding for a text chunk."""

    response = get_gemini_client().models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    return response.embeddings[0].values


def ingest_document(
    file_path: Path,
    strategy: str = "paragraph",
) -> None:
    """Extract, chunk, embed, and store a document in Chroma."""

    text = extract_text(file_path)

    if strategy == "paragraph":
        chunks = chunk_text_by_paragraph(text)

    elif strategy == "fixed":
        chunks = chunk_text(text)

    else:
        raise ValueError("Unsupported chunking strategy.")

        # Determine which PDF pages each chunk belongs to.
    chunk_pages = [[] for _ in chunks]

    if file_path.suffix.lower() == ".pdf":
        pages = extract_pdf_pages(file_path)

        page_ranges = []
        current_position = 0

        for page in pages:
            page_text = page["text"]
            page_start = current_position
            page_end = page_start + len(page_text)

            page_ranges.append(
                (
                    page["page"],
                    page_start,
                    page_end,
                )
            )

            current_position = page_end + 1

        for index, chunk in enumerate(chunks):
            chunk_start = text.find(chunk)

            if chunk_start == -1:
                continue

            chunk_end = chunk_start + len(chunk)

            for page_number, page_start, page_end in page_ranges:
                if chunk_start < page_end and chunk_end > page_start:
                    chunk_pages[index].append(page_number)

    embeddings = [
        generate_embedding(chunk)
        for chunk in chunks
    ]

    add_chunks(
        chunks=chunks,
        embeddings=embeddings,
        filename=file_path.name,
        strategy=strategy,
        pages=chunk_pages,
    )

    print(f"Ingested: {file_path.name}")
    print(f"Strategy: {strategy}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embeddings: {len(embeddings)}")


if __name__ == "__main__":

    file_path = Path(
        "uploads/Jesse Osifade - (Q2).pdf"
    )

    print("\n--- Paragraph Strategy ---")

    ingest_document(
        file_path=file_path,
        strategy="paragraph",
    )

    print("\n--- Fixed-Size Strategy ---")

    ingest_document(
        file_path=file_path,
        strategy="fixed",
    )
