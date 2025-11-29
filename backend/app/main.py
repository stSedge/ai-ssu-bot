import os

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator
from pydantic import BaseModel
from qdrant_client import QdrantClient

from upd_qdrant import update_qdrant
from search import search_qdrant

import uvicorn
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from app.core.database import database, metadata
from app.core.config import settings
from app.api import ssu_bot_api
from app.api import health_api

from app.schema.message_schema import MessageCreate, MessageRead
from app.api.depends import message_service
from app.core.exception.session_exception import SessionNotFound
from fastapi import APIRouter, HTTPException, status
from app.schema.dto.send_query_dto import SendQueryDto

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchQuery(BaseModel):
    query: str 

qdrant_client: QdrantClient | None = None


# Здесь можно подключить БД, кеш, и т.д.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global qdrant_client

    try:
        qdrant_client = QdrantClient(
            host=os.environ["QDRANT_HOST"], 
            port=os.environ["QDRANT_PORT"],
            timeout=180)
        logger.info("Connected to Qdrant")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
    # Выполняем рефлексию базы данных
    async with database.engine.begin() as conn:
        await conn.run_sync(metadata.reflect, views=True)

    yield

    if qdrant_client:
        qdrant_client = None
        logger.info("Qdrant client closed")


def create_app() -> FastAPI:
    app_options = {}
    app = FastAPI(lifespan=lifespan, root_path=settings.ROOT_PATH, **app_options)
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(ssu_bot_api.router)
    app.include_router(health_api.router)

    @app.get("/qdrant-check")
    async def qdrant_check():
        info = qdrant_client.get_collections()
        return {"qdrant_collections": info.model_dump()}

    @app.post("/update-qdrant")
    async def update_qdrant_endpoint():
        global qdrant_client
        if not qdrant_client:
            return {"error": "Qdrant client is not initialized"}
        result = await asyncio.to_thread(update_qdrant, qdrant_client)
        return result

    @app.post("/search-qdrant")
    async def search_qdrant_endpoint(search_query: SearchQuery):
        global qdrant_client
        if not qdrant_client:
            return {"error": "Qdrant client is not initialized"}
        result = await asyncio.to_thread(search_qdrant, search_query.query, qdrant_client)
        return result

    @app.post("/sendQuery", response_model=MessageRead)
    async def send_query(request: SendQueryDto):
        
        global qdrant_client
        try:
            async with database.session() as session:
                new_message = await message_service.process_user_query(
                    session=session,
                    dto=request,
                    qdrant_client=qdrant_client
                )
        except SessionNotFound as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
        return new_message

    return app


app = create_app()


async def run() -> None:
    config = uvicorn.Config("app.main:app", host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run())
