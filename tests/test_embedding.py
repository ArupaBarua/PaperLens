from langchain_huggingface import HuggingFaceEmbeddings

from backend.services.embedding_generator import get_embedding_model


def test_get_embedding_model_returns_embedding_model():
    """
    Test that the embedding function returns a
    HuggingFaceEmbeddings instance.
    """

    embedding_model = get_embedding_model()

    assert isinstance(
        embedding_model,
        HuggingFaceEmbeddings
    )


def test_embedding_model_generates_embedding():
    """
    Test that the embedding model can generate
    an embedding for a piece of text.
    """

    embedding_model = get_embedding_model()

    embedding = embedding_model.embed_query(
        "This is a test sentence."
    )

    assert embedding is not None
    assert len(embedding) > 0


def test_embedding_dimension():
    """
    Test that the embedding model produces vectors
    with the expected dimension.

    BAAI/bge-base-en-v1.5 produces 768-dimensional
    embeddings.
    """

    embedding_model = get_embedding_model()

    embedding = embedding_model.embed_query(
        "This is a test sentence."
    )

    assert len(embedding) == 768


def test_embedding_is_normalized():
    """
    Test that embeddings are normalized to approximately
    unit length.
    """

    embedding_model = get_embedding_model()

    embedding = embedding_model.embed_query(
        "This is a test sentence."
    )

    magnitude = sum(
        value ** 2
        for value in embedding
    ) ** 0.5

    assert abs(magnitude - 1.0) < 1e-5