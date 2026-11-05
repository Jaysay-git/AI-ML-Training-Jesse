from pathlib import Path

import pymupdf
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_current_user
from app.database.models import User
from app.agent.rag import ingest_uploaded_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024


def extract_document_text(content: bytes, extension: str) -> str:
    """Extract readable text from an uploaded PDF or TXT file."""

    if extension == ".txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The TXT file must use UTF-8 encoding.",
            )

    elif extension == ".pdf":
        try:
            with pymupdf.open(stream=content, filetype="pdf") as pdf:
                text = "\n".join(
                    page.get_text() for page in pdf
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The PDF file could not be read.",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported.",
        )

    text = text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No readable text was found. "
                "Scanned PDFs without selectable text are not supported."
            ),
        )

    return text


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload and privately index a PDF or TXT document."""

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 5 MB.",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    extracted_text = extract_document_text(content, extension)

    try:
        result = ingest_uploaded_document(
            text=extracted_text,
            filename=filename,
            user_id=current_user.id,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Document indexing is temporarily unavailable. "
                "Check the Gemini embedding configuration and try again."
            ),
        )

    return {
        "status": "success",
        "message": "Document uploaded and indexed successfully.",
        **result,
    }
