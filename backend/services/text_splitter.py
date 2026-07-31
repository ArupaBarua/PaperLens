from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def split_sections(sections: dict[str, str],
                   session_id: int,
                   paper_name: str) -> list[Document]:
    """
    Splits each section into smaller chunks.
    Each chunk is stored as a LangChain Document
    with metadata describing its origin.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    documents = []
    chunk_no = 1

    for section, content in sections.items():

        chunks = splitter.split_text(content)

        for chunk in chunks:

            document = Document(
                page_content=chunk,
                metadata={
                    "session_id": session_id,
                    "paper_name": paper_name,
                    "section": section,
                    "chunk_no": chunk_no
                }
            )
            
            documents.append(document)
            chunk_no += 1

    logger.info(f"Created {len(documents)} chunks.")

    return documents

        
