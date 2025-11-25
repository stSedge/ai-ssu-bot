from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class SessionBase(BaseModel):
    is_active: bool = True


class SessionCreate(SessionBase):
    pass


class SessionRead(SessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime
