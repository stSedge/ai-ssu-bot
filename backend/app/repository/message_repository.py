from typing import Type, List
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.message import Message
from app.schema.message_schema import MessageCreate, MessageRead
from app.core.exception.message_exception import MessageNotFound


class MessageRepository:
    _collection: Type[Message] = Message

    async def create_message(self, session: AsyncSession, message: MessageCreate) -> MessageRead:
        query = insert(self._collection).values(
            session_id=message.session_id,
            content=message.content,
            answer=message.answer
        ).returning(self._collection)

        created_message = await session.scalar(query)
        await session.commit()
        return MessageRead.model_validate(obj=created_message)

    async def get_messages_by_session(self, session: AsyncSession, session_id: str) -> List[MessageRead]:
        query = select(self._collection).where(self._collection.session_id == session_id)
        result = await session.scalars(query)
        messages = result.all()

        if not messages:
            raise MessageNotFound(_id=session_id)

        return [MessageRead.model_validate(obj=msg) for msg in messages]
