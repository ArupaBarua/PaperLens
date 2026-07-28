from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from backend.database.models import ChatSession, ChatMessage
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_session(db: Session, title: str) -> ChatSession:
    """
    Creates a new chat session
    """

    session = ChatSession(
        title=title
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"Created chat session (id={session.id})")

    return session

def get_session(db: Session, session_id: int) -> ChatSession | None:
    """
    Returns a chat session by its ID
    """

    session = db.get(ChatSession, session_id)

    return session

def get_all_sessions(db: Session) -> list[ChatSession]:
    """
    Returns all chat sessions ordered by newest first
    """

    statement = (
        select(ChatSession).order_by(ChatSession.created_at.desc())
    )

    sessions = db.scalars(statement).all()

    return sessions

def update_session_title(
        db: Session,
        session_id: int,
        new_title: str
) -> ChatSession | None:
    """
    Update the title of a chat session
    """

    session = db.get(ChatSession, session_id)

    if session is None:
        return None

    session.title = new_title

    db.commit()
    db.refresh(session)

    logger.info(f"Updated title of session id {session_id}")

    return session

def delete_session(
        db: Session,
        session_id: int
) -> bool:
    """
    Deletes a chat session and all its messages
    """

    session = db.get(ChatSession, session_id)

    if session is None:
        return False

    db.delete(session)
    db.commit()

    logger.info(f"Deleted chat session id = {session_id}")

    return True

def add_message(
        db: Session,
        session_id: int,
        role: str,
        content: str
) -> ChatMessage:
    """
    Adds a new message to a chat session
    """

    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    logger.info(f"Added {role} message to session {session_id}")

    return message

def get_messages(db: Session, session_id: int) -> list[ChatMessage]:
    """Returns all messages of a chat session in chronological order"""

    statement = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )

    messages = db.scalars(statement).all()

    return messages

def delete_all_sessions(db: Session) -> None:
    """
    Deletes all chat sessions and their messages
    """

    statement = select(ChatSession)
    sessions = db.scalars(statement).all()

    for session in sessions:
        db.delete(session)

    db.commit()

    logger.info("Deleted all chat sessions")
    