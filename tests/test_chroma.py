from unittest.mock import Mock, patch

from langchain_core.documents import Document

from backend.services.chroma_manager import ChromaManager


@patch(
    "backend.services.chroma_manager.Chroma"
)
@patch(
    "backend.services.chroma_manager.get_embedding_model"
)
def test_chroma_manager_initializes(
    mock_get_embedding_model,
    mock_chroma
):
    """
    Test that ChromaManager initializes the
    embedding model and Chroma vector store.
    """

    embedding_model = Mock()

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    manager = ChromaManager()

    mock_get_embedding_model.assert_called_once()

    mock_chroma.assert_called_once()

    assert manager.embedding_model == embedding_model
    assert manager.vector_store == mock_chroma.return_value


@patch(
    "backend.services.chroma_manager.Chroma"
)
@patch(
    "backend.services.chroma_manager.get_embedding_model"
)
def test_add_documents(
    mock_get_embedding_model,
    mock_chroma
):
    """
    Test that documents are passed to the Chroma
    vector store with generated IDs.
    """

    manager = ChromaManager()

    documents = [
        Document(
            page_content="Document one.",
            metadata={"session_id": 1}
        ),
        Document(
            page_content="Document two.",
            metadata={"session_id": 1}
        )
    ]

    manager.add_documents(documents)

    vector_store = mock_chroma.return_value

    vector_store.add_documents.assert_called_once()

    call_kwargs = (
        vector_store.add_documents.call_args.kwargs
    )

    assert call_kwargs["documents"] == documents

    assert len(call_kwargs["ids"]) == 2

    assert all(
        isinstance(document_id, str)
        for document_id in call_kwargs["ids"]
    )


@patch(
    "backend.services.chroma_manager.Chroma"
)
@patch(
    "backend.services.chroma_manager.get_embedding_model"
)
def test_retrieve(
    mock_get_embedding_model,
    mock_chroma
):
    """
    Test that retrieve performs similarity search
    using the correct query, session ID and k.
    """

    documents = [
        Document(
            page_content="Relevant document.",
            metadata={"session_id": 1}
        )
    ]

    vector_store = mock_chroma.return_value

    vector_store.similarity_search.return_value = (
        documents
    )

    manager = ChromaManager()

    result = manager.retrieve(
        query="What is the proposed method?",
        session_id=1,
        k=5
    )

    vector_store.similarity_search.assert_called_once_with(
        query="What is the proposed method?",
        k=5,
        filter={"session_id": 1}
    )

    assert result == documents


@patch(
    "backend.services.chroma_manager.Chroma"
)
@patch(
    "backend.services.chroma_manager.get_embedding_model"
)
def test_retrieve_returns_empty_list(
    mock_get_embedding_model,
    mock_chroma
):
    """
    Test that retrieve correctly handles a query
    that returns no documents.
    """

    vector_store = mock_chroma.return_value

    vector_store.similarity_search.return_value = []

    manager = ChromaManager()

    result = manager.retrieve(
        query="Unrelated query",
        session_id=99
    )

    assert result == []


@patch(
    "backend.services.chroma_manager.Chroma"
)
@patch(
    "backend.services.chroma_manager.get_embedding_model"
)
def test_delete_documents(
    mock_get_embedding_model,
    mock_chroma
):
    """
    Test that all documents belonging to a session
    are deleted using the correct filter.
    """

    manager = ChromaManager()

    manager.delete_documents(
        session_id=7
    )

    vector_store = mock_chroma.return_value

    vector_store.delete.assert_called_once_with(
        where={
            "session_id": 7
        }
    )