from unittest.mock import patch

from backend.services.intent_detector import (
    IntentDetector,
    Intent
)


def test_build_prompt():

    detector = IntentDetector()

    messages = detector.build_prompt(
        query="What dataset does the paper use?"
    )

    assert len(messages) == 2

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    assert (
        messages[1]["content"]
        == "What dataset does the paper use?"
    )

    assert "paper_qa" in messages[0]["content"]
    assert "paper_summary" in messages[0]["content"]
    assert "paper_comparison" in messages[0]["content"]
    assert "figure_question" in messages[0]["content"]
    assert "general" in messages[0]["content"]
    assert "greeting" in messages[0]["content"]


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_paper_qa(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "paper_qa"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="What dataset does the paper use?"
    )

    assert result == Intent.PAPER_QA


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_paper_summary(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "paper_summary"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="Summarize the paper."
    )

    assert result == Intent.PAPER_SUMMARY


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_paper_comparison(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "paper_comparison"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="Compare the two papers."
    )

    assert result == Intent.PAPER_COMPARISON


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_figure_question(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "figure_question"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="What does Figure 1 show?"
    )

    assert result == Intent.FIGURE_QUESTION


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_general(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "general"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="What is machine learning?"
    )

    assert result == Intent.GENERAL


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_greeting(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "greeting"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="Hello!"
    )

    assert result == Intent.GREETING


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_normalizes_response(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        " Paper QA "
    )

    detector = IntentDetector()

    result = detector.detect(
        query="What is the methodology?"
    )

    assert result == Intent.PAPER_QA


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_normalizes_hyphen(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "paper-qa"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="Explain the methodology."
    )

    assert result == Intent.PAPER_QA


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_unknown_intent_returns_general(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "something_else"
    )

    detector = IntentDetector()

    result = detector.detect(
        query="Some question"
    )

    assert result == Intent.GENERAL


@patch(
    "backend.services.intent_detector.GemmaClient"
)
def test_detect_calls_llm_with_messages(mock_gemma):

    mock_gemma.return_value.generate_response.return_value = (
        "figure_question"
    )

    detector = IntentDetector()

    query = "What does Figure 2 show?"

    detector.detect(query=query)

    mock_gemma.return_value.generate_response.assert_called_once()

    call_kwargs = (
        mock_gemma.return_value.generate_response.call_args.kwargs
    )

    messages = call_kwargs["messages"]

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == query