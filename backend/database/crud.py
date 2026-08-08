from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from backend.database.models import ChatSession, ChatMessage, Paper, Figure
from backend.schemas.figure import FigureInfo
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
        logger.warning(f"Session id ({session_id}) is not found")
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
        logger.warning(f"Paper id ({paper_id}) is not found")
        return False

    db.delete(paper)
    db.commit()

    logger.info(f"Delted paper (id={paper_id})")

    return True


def update_conversation_summary(
    db: Session,
    session_id: int,
    summary: str
) -> ChatSession | None:
    """
    Updates the conversation summary for a chat session.
    """

    session = get_session(
        db=db,
        session_id=session_id
    )

    if session_id is None:
        logger.error(f"Session not found for session id {session_id}")
        raise ValueError(f"Session not found for session id {session_id}")

    session.conversation_summary = summary

    db.commit()

    db.refresh(session)

    logger.info(f"Updated conversation summary for session id ({session_id})")

    return session


def delete_oldest_messages(
        db: Session, 
        session_id: int,
        limit: int
) -> None:
    """
    Deletes the oldest messages from a chat session.
    """
    session = get_session(db=db, session_id=session_id)

    if session is None:
        logger.error(f"Session not found for session id {session_id}")
        raise ValueError(f"Session not found for session id {session_id}")

    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    ).all()

    for message in messages:
        db.delete(message)

    db.commit()


def save_figures(db: Session,
                 figures: list[FigureInfo]) -> None:
    """
    Saves extracted figures to the database.
    """

    for figure in figures:

        db.add(
            Figure(
                session_id=figure.session_id,
                paper_name=figure.paper_name,
                page_number=figure.page_number,
                figure_number=figure.figure_number,
                figure_caption=figure.figure_caption,
                image_path=figure.image_path
            )
        )
    db.commit()

    logger.info(f"Saved {len(figures)} figures to the database")

    for figure in figures:
        print(
            figure.figure_number,
            figure.figure_caption
        )


def get_figure_by_number(
    db: Session,
    session_id: int,
    figure_number: str
) -> Figure | None:
    """
    Retrieves a figure by its figure number.
    """

    statement = (
        select(Figure)
        .where(
            Figure.session_id == session_id,
            Figure.figure_number == figure_number
        )
    )

    figure = db.scalar(statement)

    if figure is None:

        logger.warning(f"Figure {figure_number} not found for session {session_id}")

    else:

        logger.info(f"Retrieved Figure {figure_number} from session {session_id}")

    return figure


def get_figure_by_caption(
    db: Session,
    session_id: int,
    caption: str 
) -> Figure | None:
    """
    Retrieves a figure by matching its caption.
    """

    statement = (
        select(Figure)
        .where(Figure.session_id==session_id,
               Figure.figure_caption.ilike(f"%{caption}")
               )
    )

    figure = db.scalars(statement).first()

    if figure is None:
        logger.warning(
            f"No figure found with caption containing "
            f"'{caption}' in session {session_id}."
        )

    else:
        logger.info(
            f"Retrieved figure "
            f"'{figure.figure_number}' "
            f"using caption search."
        )

    return figure
