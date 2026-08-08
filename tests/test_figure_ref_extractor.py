from unittest.mock import patch

from backend.services.figure_ref_extractor import (
    FigureReferenceExtractor,
    FigureReferenceType
)


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_figure_number(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "NUMBER:1"
    )

    extractor = FigureReferenceExtractor()

    result = extractor.extract(
        query="What does Figure 1 show?"
    )

    assert result == (
        FigureReferenceType.NUMBER,
        "1"
    )


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_figure_number_with_period(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "NUMBER:3.2."
    )

    extractor = FigureReferenceExtractor()

    result = extractor.extract(
        query="Explain Fig. 3.2."
    )

    assert result == (
        FigureReferenceType.NUMBER,
        "3.2"
    )


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_figure_caption(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "CAPTION:system architecture"
    )

    extractor = FigureReferenceExtractor()

    result = extractor.extract(
        query="Explain the system architecture figure."
    )

    assert result == (
        FigureReferenceType.CAPTION,
        "system architecture"
    )


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_none(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "NONE"
    )

    extractor = FigureReferenceExtractor()

    result = extractor.extract(
        query="What is the main contribution of this paper?"
    )

    assert result is None


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_none_case_insensitive(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "none"
    )

    extractor = FigureReferenceExtractor()

    result = extractor.extract(
        query="Tell me about the methodology."
    )

    assert result is None


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_unexpected_output(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "I think the user means Figure 2."
    )

    extractor = FigureReferenceExtractor()

    result = extractor.extract(
        query="What does the figure show?"
    )

    assert result is None


@patch(
    "backend.services.figure_ref_extractor.GemmaClient"
)
def test_extract_calls_llm_with_query(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "NUMBER:2"
    )

    extractor = FigureReferenceExtractor()

    extractor.extract(
        query="What does Figure 2 show?"
    )

    mock_gemma.return_value.generate_response.assert_called_once()

    call_kwargs = (
        mock_gemma.return_value.generate_response.call_args.kwargs
    )

    messages = call_kwargs["messages"]

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "What does Figure 2 show?"