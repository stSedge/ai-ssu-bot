from typing import Type, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.faq import FAQ
from app.schema.faq_schema import FAQRead
from app.core.exception.faq_exception import FAQNotFound


class FAQRepository:
    _collection: Type[FAQ] = FAQ

    async def get_all_faq(self, session: AsyncSession) -> List[FAQRead]:
        query = select(self._collection)
        result = await session.scalars(query)
        return [FAQRead.model_validate(obj=faq) for faq in result.all()]

    async def get_by_id(self, session: AsyncSession, faq_id: int) -> FAQRead:
        query = select(self._collection).where(self._collection.id == faq_id)
        result = await session.scalar(query)
        if not result:
            raise FAQNotFound(_id=faq_id)
        return FAQRead.model_validate(obj=result)
