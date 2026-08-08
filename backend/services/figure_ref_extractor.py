from enum import Enum

from backend.services.gemma_client import GemmaClient
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class FigureReferenceType(Enum):

    NUMBER = "number"
    CAPTION = "caption"

class FigureReferenceExtractor:
    """
    Uses an LLM to determine user's figure reference.

    It returns either:
    - (FigureReferenceType.NUMBER, "<figure_number>")
    - (FigureReferenceType.CAPTION, "<caption_phrase>")
    """

    def __init__(self):
        self.client = GemmaClient()


    def extract(
        self,
        query: str,
    ) -> tuple[FigureReferenceType, str] | None:

        system_message = """
You are an information extraction assistant.

Your task is to extract the exact figure reference mentioned in the user's query.

The figure reference is either:
- the figure number, or
- the figure caption/title.

Return EXACTLY one of the following formats:

NUMBER:<figure_number>

CAPTION:<caption_phrase>

NONE

Rules:
- If the user refers to a figure by number (e.g. Figure 3.2., Fig. 1., Figure 5., figure 3., fig 2., fig. 2.), return:
NUMBER:<figure_number>

Examples:
NUMBER:3.2
NUMBER:1

- If the user refers to a figure by its title or caption, return:
CAPTION:<caption_phrase>

Examples:
CAPTION:system architecture
CAPTION:training pipeline
CAPTION:BiLSTM model

- Return only one line.
- Do not explain anything.
- Do not use quotation marks.
- If no figure reference can be identified, return:
NONE
""".strip()

        user_message = query

        messages = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = self.client.generate_response(messages=messages).strip()
        response = response.rstrip(".").strip()

        if response.upper() == "NONE":

            logger.info("No figure reference identified")

            return None

        if response.upper().startswith("NUMBER:"):

            figure_number = response.removeprefix("NUMBER:").strip()

            logger.info(f"Extracted figure number: {figure_number}")

            return (
                FigureReferenceType.NUMBER,
                figure_number
            )

        if response.upper().startswith("CAPTION:"):

            caption = response.removeprefix("CAPTION:").strip()

            logger.info(f"Extracted figure caption: {caption}")

            return (
                FigureReferenceType.CAPTION,
                caption    
            )

        logger.warning(f"Unexpected LLM output: {response}")

        return None