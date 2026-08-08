from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    BackgroundTasks
)
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.crud import get_papers, delete_paper

from backend.schemas.upload import PaperResponse, UploadResponse
from backend.services.paper_manager import upload_paper, process_paper
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

@router.post(
    "/{session_id}",
    response_model=UploadResponse
)
def upload(
    session_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Receives a PDF uploaded by the user, delegates the upload
    process to paper_manager, and returns information about the
    uploaded paper.
    """

    try:
        paper = upload_paper(
            db=db,
            session_id=session_id,
            file=file
        )

        background_tasks.add_task(
            process_paper,
            db=db,
            session_id=session_id,
            paper_name=paper.filename,
            file_path=Path(paper.file_path)
        )

        logger.info(f"Uploaded '{paper.filename}'")

        return UploadResponse(
            message="Paper uploaded successfully",
            paper=paper
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/{session_id}",
    response_model=list[PaperResponse]
)
def get_uploaded_papers(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns all papers uploaded to a chat session.
    """

    papers = get_papers(
        db=db,
        session_id=session_id
    )

    logger.info(
        f"Retrieved {len(papers)} papers for session {session_id}"
    )

    return papers


@router.delete(
    "/{paper_id}",
    status_code=204
)
def remove_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    Deletes a paper from the database.
    """

    deleted = delete_paper(
        db=db,
        paper_id=paper_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    logger.info(
        f"Deleted paper {paper_id}"
    )