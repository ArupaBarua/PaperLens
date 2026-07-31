from langchain_huggingface import HuggingFaceEmbeddings

from backend.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Loads the embedding model used throughout project.
    """

    embedding_model = HuggingFaceEmbeddings(
        model_name = settings.EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    logger.info(f"Loaded embedding model '{settings.EMBEDDING_MODEL}'")

    return embedding_model