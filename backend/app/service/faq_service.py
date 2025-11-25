from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.faq_repository import FAQRepository
from app.schema.faq_schema import FAQRead


class FAQService:
    def __init__(self, repo: FAQRepository) -> None:
        self.repo: FAQRepository = repo

    async def get_all_faq(self, session: AsyncSession) -> List[FAQRead]:
        result: List[FAQRead] = await self.repo.get_all_faq(session=session)
        return result

    async def get_by_id(self, session: AsyncSession, faq_id: int) -> FAQRead:
        result: FAQRead = await self.repo.get_by_id(session=session, faq_id=faq_id)
        return result
