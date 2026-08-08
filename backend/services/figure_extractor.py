import base64
import json
import re
from pathlib import Path
from uuid import uuid4
import fitz

from backend.config import settings
from backend.schemas.figure import FigureInfo
from backend.services.vision_client import VisionClient
from backend.utils.logger import setup_logger


logger = setup_logger(__name__)


class FigureExtractor:
    """
    Extracts figures from a PDF.

    PyMuPDF is responsible for:
        - finding embedded images
        - extracting the original image
        - obtaining image coordinates
        - rendering the page with the target image highlighted

    Vision model is responsible for:
        - identifying the figure number
        - identifying the corresponding figure caption

    The entire page is sent to the vision model with the
    target image highlighted. This allows the vision model
    to understand the page layout and associate the correct
    caption with the target figure.
    """

    def __init__(self):

        self.image_directory = Path(
            settings.IMAGE_DIR
        )

        self.image_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.vision_client = VisionClient()

    def save_image(
        self,
        document: fitz.Document,
        xref: int,
        session_id: int,
        page_number: int,
        image_index: int
    ) -> str:
        """
        Extracts the original embedded image from the PDF
        and saves it to disk.

        Returns:
            Path to the saved image.
        """

        image_data = document.extract_image(
            xref=xref
        )

        image_bytes = image_data["image"]
        extension = image_data["ext"]

        filename = (
            f"session_{session_id}_"
            f"page_{page_number}_"
            f"image_{image_index}_"
            f"{uuid4().hex[:8]}."
            f"{extension}"
        )

        image_path = (
            self.image_directory /
            filename
        )

        with open(
            image_path,
            "wb"
        ) as file:

            file.write(image_bytes)

        return str(image_path)


    def get_image_rect(
        self,
        page: fitz.Page,
        xref: int
    ) -> fitz.Rect | None:
        """
        Gets the bounding box of an embedded image
        on the current page.

        PyMuPDF's get_image_rects() returns the locations
        where the image is displayed on the page.

        For now, the first occurrence is used.
        """

        image_rects = page.get_image_rects(
            xref
        )

        if not image_rects:

            return None

        return image_rects[0]

 
    def render_page_with_highlight(
        self,
        page: fitz.Page,
        image_rect: fitz.Rect
    ) -> str:
        """
        Renders the entire PDF page and highlights the
        target image using its PyMuPDF bounding box.

        The rectangle exists only temporarily and is
        not saved into the PDF.

        Returns:
            Base64 encoded PNG.
        """

        annotation = page.add_rect_annot(
            image_rect
        )

        annotation.set_colors(
            stroke=(1, 0, 0)
        )

        annotation.set_border(
            width=3
        )

        annotation.update()

        try:

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False,
                annots=True
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

        finally:

            page.delete_annot(
                annotation
            )

        return base64.b64encode(
            image_bytes
        ).decode("utf-8")


    def build_vision_prompt(self) -> str:
        """
        Builds the system prompt used by the vision model.
        """

        return """
You are analyzing a scientific research paper page.

A RED RECTANGLE marks exactly ONE target image.

You MUST identify ONLY the image INSIDE the RED RECTANGLE.

Do NOT choose a figure based on its position, number, or proximity
to another figure.

First locate the RED RECTANGLE.
Then identify the figure/image completely enclosed by that rectangle.
Then find the caption that belongs to THAT image.

The caption may be below the image and may extend horizontally
beyond the image's bounding box.

If the red rectangle surrounds the image containing a graph,
diagram, or chart, that image is the target regardless of which
figure number you think it has.

Return:

{
    "figure_number": number,
    "figure_caption": caption
}

Return ONLY valid JSON.
""".strip()


    def identify_figure(
        self,
        page: fitz.Page,
        image_rect: fitz.Rect,
        page_number: int,
        image_index: int
    ) -> tuple[str | None, str | None]:
        """
        Sends the entire page to the vision model with the
        target image highlighted.

        Returns:
            figure_number, figure_caption
        """

        logger.info(
            f"Analyzing image {image_index} "
            f"on page {page_number} with vision model."
        )

        encoded_page = (
            self.render_page_with_highlight(
                page=page,
                image_rect=image_rect
            )
        )

        system_message = (
            self.build_vision_prompt()
        )

        user_message = [
            {
                "type": "text",
                "text": (
                    "Find the image enclosed by the RED RECTANGLE. "
                    "Return the figure number and complete caption "
                    "belonging to that highlighted image."
                )
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        "data:image/png;base64,"
                        f"{encoded_page}"
                    )
                }
            }
        ]

        response = (
            self.vision_client.generate_response(
                system_message=system_message,
                user_message=user_message
            )
        )

        return self.parse_vision_response(
            response
        )


    def parse_vision_response(
        self,
        response: str
    ) -> tuple[str | None, str | None]:
        """
        Parses the JSON returned by the vision model.
        """

        if not response:

            logger.warning(
                "Vision model returned an empty response."
            )

            return None, None

        response = response.strip()

        response = re.sub(
            r"^```json\s*",
            "",
            response,
            flags=re.IGNORECASE
        )

        response = re.sub(
            r"\s*```$",
            "",
            response
        )

        try:

            data = json.loads(
                response
            )

        except json.JSONDecodeError:

            logger.error(
                "Failed to parse vision model response "
                f"as JSON: {response}"
            )

            return None, None

        if not isinstance(
            data,
            dict
        ):

            logger.error(
                "Vision model response is not a JSON object."
            )

            return None, None

        figure_number = data.get(
            "figure_number"
        )

        figure_caption = data.get(
            "figure_caption"
        )

        if figure_number is not None:

            figure_number = str(
                figure_number
            ).strip()

        if figure_caption is not None:

            figure_caption = str(
                figure_caption
            ).strip()

        return (
            figure_number,
            figure_caption
        )


    def extract(
        self,
        pdf_path: str,
        session_id: int,
        paper_name: str
    ) -> list[FigureInfo]:
        """
        Extracts all figures from a PDF.

        For every embedded image:

            1. Get the image xref.
            2. Get its bounding box using get_image_rects().
            3. Extract and save the original image.
            4. Render the entire page.
            5. Highlight the target image.
            6. Send the highlighted page to the vision model.
            7. Extract figure number and caption.
            8. Create FigureInfo.
        """

        figures = []

        with fitz.open(
            pdf_path
        ) as document:

            for page_number, page in enumerate(
                document,
                start=1
            ):

                images = page.get_images(
                    full=True
                )

                logger.info(
                    f"Found {len(images)} images "
                    f"on page {page_number}."
                )

                if not images:
                    continue

                for image_index, image in enumerate(
                    images,
                    start=1
                ):

                    xref = image[0]

                    image_rect = (
                        self.get_image_rect(
                            page=page,
                            xref=xref
                        )
                    )

                    if image_rect is None:

                        logger.warning(
                            f"Could not determine bounding box "
                            f"for image {image_index} "
                            f"on page {page_number}."
                        )

                        continue

                    logger.info(
                        f"Image {image_index} "
                        f"on page {page_number}: "
                        f"bbox={image_rect}"
                    )

                    image_path = (
                        self.save_image(
                            document=document,
                            xref=xref,
                            session_id=session_id,
                            page_number=page_number,
                            image_index=image_index
                        )
                    )

                    figure_number, figure_caption = (
                        self.identify_figure(
                            page=page,
                            image_rect=image_rect,
                            page_number=page_number,
                            image_index=image_index
                        )
                    )

                    figure = FigureInfo(
                        session_id=session_id,
                        paper_name=paper_name,
                        page_number=page_number,
                        figure_number=figure_number,
                        figure_caption=figure_caption,
                        image_path=image_path
                    )

                    figures.append(
                        figure
                    )

                    logger.info(
                        f"Image {image_index} "
                        f"on page {page_number}: "
                        f"Figure={figure_number}, "
                        f"Caption={figure_caption}"
                    )

        logger.info(
            f"Extracted {len(figures)} figures "
            f"from {paper_name}"
        )

        return figures