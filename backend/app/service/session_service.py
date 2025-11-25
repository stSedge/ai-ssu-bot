from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.session_schema import SessionRead
from app.repository.session_repository import SessionRepository


class SessionService:
    def __init__(self, repo: SessionRepository) -> None:
        self.repo: SessionRepository = repo

    async def create_session(self, session: AsyncSession) -> SessionRead:
        result: SessionRead = await self.repo.create_session(session)
        return result

    async def deactivate_session(self, session: AsyncSession, session_id: UUID) -> SessionRead:
        result: SessionRead = await self.repo.deactivate_session(session, session_id)
        return result
