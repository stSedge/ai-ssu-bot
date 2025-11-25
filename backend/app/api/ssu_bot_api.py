from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.api.depends import database, session_service, message_service, faq_service
from app.core.exception.session_exception import SessionNotFound
from app.core.exception.faq_exception import FAQNotFound
from app.schema.session_schema import SessionRead
from app.schema.message_schema import MessageCreate, MessageRead
from app.schema.faq_schema import FAQRead
from app.schema.dto.send_query_dto import SendQueryDto

router = APIRouter()


@router.post("/addChat", response_model=SessionRead)
async def add_chat():
    async with database.session() as session:
        new_session = await session_service.create_session(session)
    return new_session


@router.post("/sendQuery", response_model=MessageRead)
async def send_query(request: SendQueryDto):
    try:
        async with database.session() as session:
            new_message = await message_service.process_user_query(
                session=session,
                dto=request
            )
    except SessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return new_message


@router.delete("/clearChat")
async def clear_chat(sessionId: UUID):
    try:
        async with database.session() as session:
            await session_service.deactivate_session(session, sessionId)
    except SessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return {"status": "cleared"}


@router.get("/getFAQ", response_model=list[FAQRead])
async def get_all_faq():
    async with database.session() as session:
        return await faq_service.get_all_faq(session)


@router.get("/getFAQ/{id}", response_model=FAQRead)
async def get_faq_by_id(id: int):
    try:
        async with database.session() as session:
            return await faq_service.get_by_id(session, id)
    except FAQNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
