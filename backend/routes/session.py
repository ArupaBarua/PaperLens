from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.crud import (
    create_session,
    get_all_sessions,
    get_session,
    update_session_title,
    delete_session,
    delete_all_sessions
)
from backend.database.database import get_db
from backend.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionUpdate
)
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.post(
    "/",
    response_model=SessionResponse,
    status_code=201
)
def create_new_session(session: SessionCreate, 
                       db: Session = Depends(get_db)):
    """
    Creates a new chat session.
    """

    new_session = create_session(
        db=db,
        title=session.title
    )

    logger.info(f"Created session (id={new_session.id})")

    return new_session


@router.get(
    "/",
    response_model=list[SessionResponse]
)
def get_all_chat_sessions(db: Session = Depends(get_db)):
    """
    Returns all chat sessions.
    """

    sessions = get_all_sessions(db)
    logger.info(f"Retrieved {len(sessions)} sessions")

    return sessions


@router.get(
    "/{session_id}",
    response_model=SessionResponse
)
def get_single_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns a chat session by its ID.
    """

    session = get_session(db=db, session_id=session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    logger.info(f"Retrieved session (id={session_id})")

    return session


@router.put(
    "/{session_id}",
    response_model=SessionResponse
)
def rename_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates the title of a chat session.
    """

    updated_session = update_session_title(
        db=db,
        session_id=session_id,
        new_title=session_data.title
    )

    if updated_session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )
    logger.info(f"Renamed session {session_id} to '{session_data.title}'")

    return updated_session


@router.delete(
    "/{session_id}",
    status_code=204
)
def remove_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Deletes a chat session and its associated data.
    """

    deleted = delete_session(
        db=db,
        session_id=session_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    logger.info(f"Deleted session (id={session_id})")


@router.delete(
    "/",
    status_code=204
)
def remove_all_sessions(
    db: Session = Depends(get_db)
):
    """
    Deletes all chat sessions and their associated data.
    """
    
    delete_all_sessions(db)

    logger.info(
        "Deleted all chat sessions"
    )