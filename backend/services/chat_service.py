from sqlalchemy.orm import Session

from backend.database.crud import (
    get_session,
    get_messages,
    add_message
)
from backend.database.models import ChatMessage

from backend.services.chroma_manager import ChromaManager
from backend.services.retriever import Retriever
from backend.services.context_optimizer import optimize_context
from backend.services.prompt_builder import build_prompt
from backend.services.gemma_client import GemmaClient
from backend.services.conversation_memory import update_chat_conversation_summary

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

chroma_maanger = ChromaManager()

retriever = Retriever(chroma_manager=chroma_maanger)

gemma_client = GemmaClient()


def process_chat(
        db: Session,
        session_id: int,
        query: str
):
    """
    Processes a user's query through the complete
    RAG pipeline and returns the assistant response.
    """

    session = get_session(
        db=db,
        session_id=session_id
    )
    if session is None:
        raise ValueError("Session not found.")

    add_message(
        db=db,
        session_id=session_id,
        role="user",
        content=query
    )

    chat_history = get_messages(db=db, session_id=session_id)

    update_chat_conversation_summary(
        db=db,
        session_id=session_id,
        chat_history=chat_history
    )

    session = get_session(
        db=db,
        session_id=session_id
    )

    chat_history = get_messages(db=db, session_id=session_id)

    documents = retriever.retrieve(query=query, session_id=session_id)

    optimized_documents = optimize_context(documents=documents)

    messages = build_prompt(
        question=query,
        documents=optimized_documents,
        chat_history=chat_history,
        conversation_summary=session.conversation_summary
    )

    assistant_reply = gemma_client.generate_response(messages=messages)

    assistant_message = add_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=assistant_reply
    )

    logger.info(f"Processed chat for session {session_id}")

    return assistant_message