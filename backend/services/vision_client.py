import base64
from pathlib import Path
from openai import OpenAI

from backend.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
}

class VisionClient:

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        self.model = settings.VISION_MODEL


    def encode_image(
        self,
        image_path: str
    ) -> tuple[str, str]:

        path = Path(image_path)
        extension = path.suffix.lower()

        mime_type = MIME_TYPES.get(extension)

        if mime_type is None:
            raise ValueError(
                f"Unsupported image format: {extension}"
            )

        with open (path, "rb") as file:
            image = base64.b64encode(
                file.read()
            ).decode("utf-8")

        return mime_type, image


    def generate_response(
        self,
        system_message: str,
        user_message: str,
        image_path: str | None = None
    ) -> str:

        if image_path is not None:
            mime_type, image = self.encode_image(image_path=image_path)

            content = [
                {
                    "type": "text",
                    "text": user_message
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image}"
                    }
                }
            ]

        else:
            content = user_message

        messages = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": content
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        if getattr(response, "error", None):

            logger.error(response.error)

            raise RuntimeError(response.error["message"])

        answer = response.choices[0].message.content

        logger.info(f"Generated vision response")

        return answer