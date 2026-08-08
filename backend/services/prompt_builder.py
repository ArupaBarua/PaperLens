from langchain_core.documents import Document

from backend.database.models import ChatMessage
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def build_prompt(
    question: str,
    documents: list[Document],
    chat_history: list[ChatMessage],
    conversation_summary: str | None = None
) -> list[dict[str, str]]:
    """
    Builds the messages sent to the language model.
    """

    system_message  = """
You are PaperLens, an AI-powered research assistant.

Your primary purpose is to help users understand research papers, compare multiple papers, identify strengths, weaknesses, limitations, research gaps, and suggest future research directions.

Use the provided research context whenever it is relevant.

If the uploaded papers do not fully answer the user's question, use your own knowledge to provide a helpful and accurate answer. Clearly distinguish between information supported by the uploaded papers and your general knowledge whenever appropriate.

You may also answer general research, academic, technical, career, programming, machine learning, AI, and software engineering questions even when they are unrelated to the uploaded papers.

When multiple papers are available, compare them objectively and highlight similarities, differences, advantages, disadvantages, limitations, and opportunities for future work.

You may also engage in natural conversation and respond appropriately to casual greetings and general questions.

Be concise, factual, well-structured, and honest. Do not fabricate citations or claim information is present in the uploaded papers when it is not.
""".strip()

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    if conversation_summary:
        messages.append(
            {
                "role": "system",
                "content":
                    f"Previous conversation summary:\n"
                    f"{conversation_summary}"
            }
        )

    for message in chat_history:

        messages.append(
            {
                "role": message.role,
                "content": message.content
            }
        )

    context = ""

    for document in documents:

        context += (
            f"Paper: {document.metadata['paper_name']}\n"
            f"Section: {document.metadata['section']}\n\n"
            f"{document.page_content}\n\n"
        )

    user_message = f"""
Relevant Paper Context:

{context}

User Question:

{question}
""".strip()

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    logger.info("Built prompt")

    return messages