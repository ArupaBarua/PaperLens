from langchain_core.documents import Document
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def optimize_context(
        documents: list[Document]
) -> list[Document]:
    """
    Removes duplicate chunks while preserving order.
    """

    optimized_documents = []
    seen = set()

    for document in documents:

        text = document.page_content.strip()

        if text is seen:
            continue

        seen.add(text)
        optimized_documents.append(document)

    logger.info(
        f"Optimized context from "
        f"{len(documents)} to "
        f"{len(optimized_documents)} chunks"
    )

    return optimized_documents