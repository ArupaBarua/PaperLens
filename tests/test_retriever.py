from unittest.mock import Mock

from langchain_core.documents import Document

from backend.services.retriever import Retriever


def test_retrieve_returns_documents():
    """
    Test that Retriever returns the documents
    provided by ChromaManager.
    """

    documents = [
        Document(
            page_content="This is document one."
        ),
        Document(
            page_content="This is document two."
        )
    ]

    chroma_manager = Mock()

    chroma_manager.retrieve.return_value = documents

    retriever = Retriever(
        chroma_manager=chroma_manager
    )

    result = retriever.retrieve(
        query="test query",
        session_id=1
    )

    assert result == documents


def test_retrieve_calls_chroma_manager():
    """
    Test that Retriever passes the correct
    arguments to ChromaManager.
    """

    chroma_manager = Mock()

    chroma_manager.retrieve.return_value = []

    retriever = Retriever(
        chroma_manager=chroma_manager
    )

    retriever.retrieve(
        query="What is the proposed approach?",
        session_id=5
    )

    chroma_manager.retrieve.assert_called_once_with(
        query="What is the proposed approach?",
        session_id=5,
        k=10
    )


def test_retrieve_returns_empty_list_when_no_documents():
    """
    Test that Retriever correctly handles a query
    for which no documents are returned.
    """

    chroma_manager = Mock()

    chroma_manager.retrieve.return_value = []

    retriever = Retriever(
        chroma_manager=chroma_manager
    )

    result = retriever.retrieve(
        query="some unrelated query",
        session_id=1
    )

    assert result == []