import os

from docx import Document
from pypdf import PdfReader


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages).strip()


def extract_docx_text(file_path: str) -> str:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs).strip()


def extract_resume_text(
    file_path: str,
    content_type: str,
) -> str:

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    if content_type == "application/pdf":
        return extract_pdf_text(file_path)

    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return extract_docx_text(file_path)

    raise ValueError(
        "Unsupported resume file type"
    )