from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.crud import get_messages

from backend.schemas.message import (
    MessageCreate,
    MessageResponse
)
from backend.services.chat_service import process_chat
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "/{session_id}",
    response_model=MessageResponse
)
def chat(
    session_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Receives a user message, delegates processing to chat_service,
    and returns the assistant's response.
    """

    try:
        assistant_message = process_chat(
            db=db,
            session_id=session_id,
            query=message.content
        )

        logger.info(f"Processed chat for session {session_id}")

        return assistant_message

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@router.get(
    "/{session_id}/messages",
    response_model=list[MessageResponse]
)
def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns the complete conversation history of a chat session.
    """
    messages = get_messages(
        db=db,
        session_id=session_id
    )

    logger.info(f"Retrieved {len(messages)} messages for session {session_id}")

    return messages