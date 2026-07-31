from openai import OpenAI

from backend.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class GemmaClient:
    """
    Handles communication with the language model.
    """

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        logger.info("Initialized Gemma client")

    def generate_response(
        self,
        messages: list[dict[str, str]]
    ) -> str:
        """
        Generates a response from the language model.
        """

        response = self.client.chat.completions.create(
            model = settings.LLM_MODEL,
            messages=messages
        )

        assistant_response = response.choices[0].message.content.strip()

        logger.info("Generated LLM response")

        return assistant_response