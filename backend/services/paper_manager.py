from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.database.crud import add_paper, get_session
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "uploaded_papers"
UPLOAD_DIR.mkdir(exist_ok=True)

def upload_paper(
        db: Session,
        session_id: int,
        file: UploadFile
):
    """
    Uploads a paper, stores it on disk,
    and creates a database record.
    """

    # Check if the session exists
    session = get_session(
        db=db,
        session_id=session_id
    )

    if session is None:
        raise ValueError("Session not found.")

    # Original file name
    original_filename = file.filename

    # Generate a unique filename
    extension = Path(original_filename).suffix
    stored_filename = f"{uuid4()}{extension}"

    file_path = UPLOAD_DIR / stored_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    paper = add_paper(
        db=db,
        session_id=session_id,
        filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(file_path)
    )

    logger.info(f"Uploaded paper '{original_filename}' to session {session_id}")

    return paper
    