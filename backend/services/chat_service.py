from sqlalchemy.orm import Session

from backend.utils.logger import setup_logger
from backend.database.crud import (
    add_message,
    get_session
)

logger = setup_logger(__name__)

def process_chat(
        db: Session,
        session_id: int,
        message: str
):
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
        content=message
    )

    assistant_reply = (
        "RAG pipeline not implemented yet."
    )

    assistant_message=add_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=assistant_reply
    )

    logger.info(f"Processed chat for session {session_id}")

    return assistant_message