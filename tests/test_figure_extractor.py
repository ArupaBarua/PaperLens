import base64
import fitz

from unittest.mock import MagicMock, patch

from backend.services.figure_extractor import FigureExtractor


def test_get_image_rect_returns_first_rect():

    extractor = FigureExtractor()

    page = MagicMock()

    first_rect = fitz.Rect(10, 20, 100, 200)
    second_rect = fitz.Rect(200, 300, 400, 500)

    page.get_image_rects.return_value = [
        first_rect,
        second_rect
    ]

    result = extractor.get_image_rect(
        page=page,
        xref=10
    )

    assert result == first_rect

    page.get_image_rects.assert_called_once_with(10)


def test_get_image_rect_returns_none_when_not_found():

    extractor = FigureExtractor()

    page = MagicMock()

    page.get_image_rects.return_value = []

    result = extractor.get_image_rect(
        page=page,
        xref=10
    )

    assert result is None


def test_parse_vision_response():

    extractor = FigureExtractor()

    response = """
    {
        "figure_number": "Fig. 1",
        "figure_caption": "System architecture of the proposed model."
    }
    """

    result = extractor.parse_vision_response(response)

    assert result == (
        "Fig. 1",
        "System architecture of the proposed model."
    )


def test_parse_vision_response_with_markdown():

    extractor = FigureExtractor()

    response = """```json
{
    "figure_number": "Fig. 2",
    "figure_caption": "Embedding Similarity System Approach"
}
```"""

    result = extractor.parse_vision_response(response)

    assert result == (
        "Fig. 2",
        "Embedding Similarity System Approach"
    )


def test_parse_vision_response_invalid_json():

    extractor = FigureExtractor()

    result = extractor.parse_vision_response(
        "This is not valid JSON"
    )

    assert result == (
        None,
        None
    )


def test_parse_vision_response_empty():

    extractor = FigureExtractor()

    result = extractor.parse_vision_response("")

    assert result == (
        None,
        None
    )


def test_render_page_with_highlight():

    extractor = FigureExtractor()

    document = fitz.open()

    page = document.new_page(
        width=300,
        height=300
    )

    image_rect = fitz.Rect(
        50,
        50,
        150,
        150
    )

    result = extractor.render_page_with_highlight(
        page=page,
        image_rect=image_rect
    )

    assert isinstance(result, str)

    decoded = base64.b64decode(result)

    assert decoded.startswith(
        b"\x89PNG"
    )

    # Annotation should have been removed.
    assert page.first_annot is None

    document.close()


@patch(
    "backend.services.figure_extractor.VisionClient"
)
def test_identify_figure(mock_vision_client):

    extractor = FigureExtractor()

    extractor.vision_client = (
        mock_vision_client.return_value
    )

    extractor.vision_client.generate_response.return_value = """
    {
        "figure_number": "Fig. 1",
        "figure_caption": "LLM Fine-tuning System Approach"
    }
    """

    page = MagicMock()

    image_rect = fitz.Rect(
        50,
        50,
        150,
        150
    )

    with patch.object(
        extractor,
        "render_page_with_highlight",
        return_value="fake_base64_image"
    ):

        result = extractor.identify_figure(
            page=page,
            image_rect=image_rect,
            page_number=3,
            image_index=1
        )

    assert result == (
        "Fig. 1",
        "LLM Fine-tuning System Approach"
    )

    extractor.vision_client.generate_response.assert_called_once()