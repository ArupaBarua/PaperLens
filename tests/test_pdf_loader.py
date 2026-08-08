import fitz
import pytest

from backend.services.pdf_loader import load_pdf


def create_pdf(tmp_path, pages):
    """
    Creates a temporary PDF containing the
    provided text on each page.
    """

    pdf_path = tmp_path / "test.pdf"

    document = fitz.open()

    for text in pages:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            text
        )

    document.save(pdf_path)
    document.close()

    return pdf_path


def test_load_pdf_extracts_text(tmp_path):
    """
    Test that text is correctly extracted
    from a single-page PDF.
    """

    pdf_path = create_pdf(
        tmp_path,
        ["Hello, this is a test PDF."]
    )

    result = load_pdf(
        str(pdf_path)
    )

    assert "Hello, this is a test PDF." in result


def test_load_pdf_extracts_multiple_pages(tmp_path):
    """
    Test that text is extracted from all pages.
    """

    pdf_path = create_pdf(
        tmp_path,
        [
            "This is page one.",
            "This is page two.",
            "This is page three."
        ]
    )

    result = load_pdf(
        str(pdf_path)
    )

    assert "This is page one." in result
    assert "This is page two." in result
    assert "This is page three." in result


def test_load_pdf_preserves_page_separation(tmp_path):
    """
    Test that extracted pages are joined with
    newline separation.
    """

    pdf_path = create_pdf(
        tmp_path,
        [
            "Page one text.",
            "Page two text."
        ]
    )

    result = load_pdf(
        str(pdf_path)
    )

    assert "Page one text." in result
    assert "Page two text." in result
    assert "\n\n" in result


def test_load_empty_pdf(tmp_path):
    """
    Test that an empty PDF returns an empty string.
    """

    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    result = load_pdf(
        str(pdf_path)
    )

    assert result == ""


def test_load_pdf_invalid_path():
    """
    Test that loading a nonexistent PDF raises
    an appropriate exception.
    """

    with pytest.raises(
        (FileNotFoundError, RuntimeError)
    ):
        load_pdf(
            "nonexistent_file.pdf"
        )