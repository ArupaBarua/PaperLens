from langchain_core.documents import Document

from backend.config import settings
from backend.services.chroma_manager import ChromaManager
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    """
    Retrieves the most relevant document chunks
    for a user's query.
    """
    def __init__(self, chroma_manager: ChromaManager):
        self.chroma = chroma_manager

    def retrieve(self,
                 query: str, 
                 session_id: int) -> list[Document]:
        """
        Retrieves the top-k relevant document chunks.
        """

        documents = self.chroma.retrieve(
            query=query, 
            session_id=session_id,
            k= settings.TOP_K
        )

        logger.info(f"Retrieved {len(documents)} relevant chunks.")

        return documents

