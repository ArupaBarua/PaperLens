from enum import Enum

from backend.services.gemma_client import GemmaClient
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class Intent(Enum):

    PAPER_QA = "paper_qa"

    PAPER_SUMMARY = "paper_summary"

    PAPER_COMPARISON = "paper_comparison"

    FIGURE_QUESTION = "figure_question"

    GENERAL = "general"

    GREETING = "greeting"


class IntentDetector:

    def __init__(self):

        self.llm = GemmaClient()

    def build_prompt(
        self,
        query: str
    ) -> list[dict[str, str]]:

        system_message = """
You are an intent classification model.

Your task is to classify the user's query into EXACTLY ONE of the following intents.

paper_qa
paper_summary
paper_comparison
figure_question
general
greeting

Definitions:

paper_qa
- Questions about uploaded research papers.
- Questions asking for explanations of paper content.
- Questions about methods, datasets, experiments, results, limitations, future work, etc.

paper_summary
- Requests to summarize one or more uploaded papers.

paper_comparison
- Requests to compare multiple uploaded papers.

figure_question
- Questions asking about figures, diagrams, charts, images or tables from uploaded papers.

general
- Any general question unrelated to uploaded papers.

greeting
- Greetings or casual conversation such as:
Hello
Hi
Good morning
How are you?

Return ONLY the intent label.

Do not explain.

Do not include punctuation.

Do not include any other words.
""".strip()

        return [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": query
            }
        ]

    def detect(
        self,
        query: str
    ) -> Intent:

        messages = self.build_prompt(query=query)

        response = self.llm.generate_response(
            messages=messages
        )

        response = (
            response
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
)

        try:

            intent = Intent(response)

            logger.info(f"Detected intent: {intent.value}")

            return intent

        except ValueError:

            logger.warning(f"Unknown intent returned by LLM: {response}")

            return Intent.GENERAL


