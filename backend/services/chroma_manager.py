from uuid import uuid4
from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.config import settings
from backend.services.embedding_generator import get_embedding_model
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChromaManager:
    """
    Handles all interactions with the Chroma vector database.
    """

    def __init__(self):

        self.embedding_model = get_embedding_model()
        
        self.vector_store = Chroma(
            collection_name="PaperLens",
            persist_directory=str(settings.CHROMA_DB_PATH),
            embedding_function=self.embedding_model
        )
        
        logger.info("Initialized ChromaDB.")

    def add_documents(
            self,
            documents: list[Document]
    ) -> None:
        """
        Adds documents to the vector store.
        """

        ids = [str(uuid4()) for _ in documents]

        self.vector_store.add_documents(
            documents=documents,
            ids=ids
        )
        logger.info(f"Added {len(documents)} documents to ChromaDB")


    def retrieve(
        self,
        query: str,
        session_id: int,
        k: int = settings.TOP_K
    ) -> list[Document]:
        """
        Retrieves the most relevant documents for a query
        within a chat session.
        """

        documents = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter={"session_id": session_id}
        )

        logger.info(f"Retrieved {len(documents)} documents for {query} in session {session_id}")

        return documents

    def delete_documents(
            self,
            ids: list[str]
    ) -> None:
        """
        Deletes documents from the vector store.
        """

        self.vector_store.delete(ids=ids)

        logger.info(f"Deleted {len(ids)} documents from ChromaDB")