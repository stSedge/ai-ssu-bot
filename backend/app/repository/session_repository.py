from typing import Type

from uuid import UUID
from sqlalchemy import insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.session import Session
from app.schema.session_schema import SessionRead
from app.core.exception.session_exception import SessionNotFound


class SessionRepository:
    _collection: Type[Session] = Session

    async def create_session(self, session: AsyncSession) -> SessionRead:
        query = insert(self._collection).values(is_active=True).returning(self._collection)
        created_session = await session.scalar(query)
        await session.commit()
        return SessionRead.model_validate(obj=created_session)

    async def deactivate_session(self, session: AsyncSession, session_id: UUID) -> SessionRead:
        query = (
            update(self._collection)
            .where(self._collection.id == session_id)
            .values(is_active=False)
            .returning(self._collection)
        )
        updated_session = await session.scalar(query)
        await session.commit()

        if not updated_session:
            raise SessionNotFound(_id=session_id)

        return SessionRead.model_validate(obj=updated_session)

    # Находит активную (is_active == True) сессию по session_id. В противном случае кидает ошибку SessionNotFound
    async def check_active_session(self, session: AsyncSession, session_id: UUID) -> SessionRead:
        query = select(self._collection).where(
            self._collection.id == session_id,
            self._collection.is_active == True
        )
        result = await session.scalar(query)
        if not result:
            raise SessionNotFound(_id=session_id)
        return SessionRead.model_validate(obj=result)
