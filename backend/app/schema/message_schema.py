from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class MessageBase(BaseModel):
    content: str = Field(..., max_length=2000)
    answer: str = Field(..., max_length=3000)

class MessageCreate(MessageBase):
    session_id: UUID

class MessageRead(MessageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
