from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PaperResponse(BaseModel):
    id: int
    session_id: int
    filename: str
    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class UploadResponse(BaseModel):
    message: str
    paper: PaperResponse