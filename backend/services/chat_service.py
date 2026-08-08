from sqlalchemy.orm import Session

from backend.database.crud import (
    get_session,
    get_messages,
    add_message
)
from backend.services.chroma_manager import ChromaManager
from backend.services.retriever import Retriever
from backend.services.context_optimizer import optimize_context
from backend.services.prompt_builder import build_prompt
from backend.services.gemma_client import GemmaClient
from backend.services.conversation_memory import update_chat_conversation_summary
from backend.services.intent_detector import Intent, IntentDetector
from backend.services.figure_qa import answer as answer_figure_question

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

chroma_manager = ChromaManager()

retriever = Retriever(chroma_manager=chroma_manager)

gemma_client = GemmaClient()

intent_detector = IntentDetector()


def process_chat(
        db: Session,
        session_id: int,
        query: str
):
    """
    Processes a user's query through the PaperLens
    chat pipeline and returns the assistant response.
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

    intent = intent_detector.detect(query=query)

    logger.info(f"Intent: {intent.value}")

    if intent == Intent.FIGURE_QUESTION:

        assistant_reply = answer_figure_question(
            db=db,
            session_id=session_id,
            query=query
        )

    else:

        if intent in (
            Intent.PAPER_QA,
            Intent.PAPER_SUMMARY,
            Intent.PAPER_COMPARISON
        ):
            documents = retriever.retrieve(
                query=query,
                session_id=session_id
            )
            optimized_documents = optimize_context(
                documents=documents
            )
        else:
            optimized_documents = []

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