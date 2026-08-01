from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from backend.database.models import ChatSession, ChatMessage, Paper
from backend.utils.logger import setup_logger
from datetime import datetime

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
        select(ChatSession).order_by(ChatSession.last_updated_at.desc())
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

    session = db.get(ChatSession, session_id)
    session.last_updated_at = datetime.utcnow()

    db.commit()

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

def add_paper(
        db: Session,
        session_id: int,
        filename: str,
        stored_filename: str,
        file_path: str
) -> Paper:
    """
    Adds a paper to a chat session
    """

    paper = Paper(
        session_id=session_id,
        filename=filename,
        stored_filename=stored_filename,
        file_path=file_path
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    logger.info(f"Added paper '{filename}' to session id={session_id}")

    return paper

def get_papers(
    db: Session,
    session_id: int,
) -> list[Paper]:
    """
    Returns all papers of a chat session
    """

    statement = (
        select(Paper).
        where(Paper.session_id==session_id)
        .order_by(Paper.uploaded_at.asc())
    )

    return db.scalars(statement).all()

def delete_paper(
    db: Session,
    paper_id: int
) -> bool:
    """
    Deletes a paper
    """

    paper = db.get(Paper, paper_id)

    if paper is None:
        return False

    db.delete(paper)
    db.commit()

    logger.info(f"Delted paper (id={paper_id})")

    return True

    