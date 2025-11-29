from typing import Any
from uuid import UUID

from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.message_repository import MessageRepository
from app.repository.session_repository import SessionRepository
from app.schema.message_schema import MessageCreate, MessageRead
from app.schema.dto.send_query_dto import SendQueryDto
from app.schema.session_schema import SessionRead

from app.search import search_qdrant
from app.service.llm_client import ask_llm

class MessageService:
    def __init__(self, repo: MessageRepository, session_repo: SessionRepository) -> None:
        self.repo: MessageRepository = repo
        self.session_repo: SessionRepository = session_repo

    async def process_user_query(
        self,
        session: AsyncSession,
        dto: SendQueryDto,
        qdrant_client: QdrantClient
    ) -> MessageRead:
        # Проверяем наличие по session_id активной сессии
        await self.session_repo.check_active_session(session=session, session_id=dto.sessionId)

        qdrant_context = search_qdrant(dto.query, qdrant_client)

        text = ""
        for el in qdrant_context:
            text += el[1] + " "
        
        print(text)
        answer = ask_llm("Ответь на этот вопрос, используя данный контекст. Не придумывай. Нет нужной информации - так и скажи. Необязательно точный ответ на вопрос, подойдет общая информация по теме. Еще не говори в начале, что согласно контексту. Просто сразу отвечай. Вопрос: " + dto.query + " | контекст: " + text)

        answer += "\n Источники: " 

        for el in qdrant_context:
            answer += el[0] + '\n'

        message_dto: MessageCreate = MessageCreate(
            session_id=dto.sessionId,
            content=dto.query,
            answer=answer
        )
        new_message: MessageRead = await self.repo.create_message(session=session, message=message_dto)
        return new_message
