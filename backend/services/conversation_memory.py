from sqlalchemy.orm import Session

from backend.config import settings

from backend.database.crud import (
    get_session,
    update_conversation_summary,
    delete_oldest_messages
)
from backend.database.models import ChatMessage

from backend.services.gemma_client import GemmaClient

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

gemma_client = GemmaClient()


def should_update_memory(
    chat_history: list[ChatMessage]
) -> bool:

    return (
        len(chat_history)
        >= settings.MEMORY_TRIGGER
    )


def build_summary_prompt(
    previous_summary: str | None,
    messages: list[ChatMessage]
) -> list[dict[str, str]]:

    system_message = """
You maintain the long-term memory of an ongoing conversation.

Your task is to produce an updated conversation summary.

The summary should preserve important information while remaining concise.

Include:
- User goals
- Important discussions
- Research papers discussed
- Conclusions reached
- Important technical details
- Unresolved questions

Ignore greetings and casual conversation.

Return only the updated conversation summary.
""".strip()

    prompt = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    if previous_summary:

        prompt.append(
            {
                "role": "system",
                "content":
                    f"Existing conversation summary:\n"
                    f"{previous_summary}"
            }
        )

    conversation = ""

    for message in messages:

        conversation += {
            f"{message.role.capitalize()}: "
            f"{message.content}\n"
        }

    prompt.append(
        {
            "role": "user",
            "content":
                f"Recent conversation:\n"
                f"{conversation}"
        }
    )

    return prompt


def generate_summary(
    previous_summary: str | None,
    messages: list[ChatMessage]
) -> str:
    """
    Generates conversation summary
    """

    prompt = build_summary_prompt(
        previous_summary=previous_summary,
        messages=messages
    )

    summary = gemma_client.generate_response(
        messages=prompt
    )

    logger.info("Generated conversation summary")

    return summary


def update_chat_conversation_summary(
        db: Session,
        session_id: int,
        chat_history: list[ChatMessage]
) -> None:
    """
    Updates the long-term conversation summary
    and removes old messages when necessary.
    """

    if not should_update_memory(chat_history=chat_history):
        return

    session = get_session(
        db=db,
        session_id=session_id
    )

    if session is None:
        raise ValueError("Session not found")

    previous_summary = session.conversation_summary

    messages_to_summarize = chat_history[
        :settings.MESSAGES_TO_SUMMARIZE
    ]

    summary = generate_summary(
        previous_summary=previous_summary,
        messages=messages_to_summarize
    )

    update_conversation_summary(
        db=db,
        session_id=session_id,
        summary=summary
    )

    delete_oldest_messages(
        db=db,
        session_id=session_id,
        limit=settings.MESSAGES_TO_SUMMARIZE
    )

    logger.info(
        f"Updated conversation memory for session {session_id}"
    )