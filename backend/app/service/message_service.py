from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.message_repository import MessageRepository
from app.repository.session_repository import SessionRepository
from app.schema.message_schema import MessageCreate, MessageRead
from app.schema.dto.send_query_dto import SendQueryDto
from app.schema.session_schema import SessionRead


class MessageService:
    def __init__(self, repo: MessageRepository, session_repo: SessionRepository) -> None:
        self.repo: MessageRepository = repo
        self.session_repo: SessionRepository = session_repo

    async def process_user_query(
        self,
        session: AsyncSession,
        dto: SendQueryDto
    ) -> MessageRead:
        # Проверяем наличие по session_id активной сессии
        await self.session_repo.check_active_session(session=session, session_id=dto.sessionId)

        message_dto: MessageCreate = MessageCreate(
            session_id=dto.sessionId,
            content=dto.query
        )
        # TODO: здесь будет логика RAG, генерации ответа

        new_message: MessageRead = await self.repo.create_message(session=session, message=message_dto)
        return new_message
