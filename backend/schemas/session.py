from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SessionCreate(BaseModel):
    title: str

class SessionUpdate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    id: int
    title: str
    conversation_summary: str | None
    created_at: datetime
    last_updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )