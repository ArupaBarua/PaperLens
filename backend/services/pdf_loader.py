import fitz
from pathlib import Path

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def load_pdf(pdf_path: str) -> str:
    """
    Extracts raw text from a PDF file.
    """

    pages = []

    with fitz.open(pdf_path) as document:
        for page in document:
            pages.append(page.get_text())

    text = "\n".join(pages)

    logger.info(f"Extracted text from '{Path(pdf_path).name}'")

    return text
