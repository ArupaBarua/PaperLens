from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SessionCreate(BaseModel):
    title: str

class SessionUpdate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    last_updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )