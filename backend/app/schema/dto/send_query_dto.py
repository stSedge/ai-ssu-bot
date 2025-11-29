from pydantic import BaseModel
from uuid import UUID


class SendQueryDto(BaseModel):
    query: str
    sessionId: UUID
