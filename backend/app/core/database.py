from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict

from sqlalchemy import JSON, MetaData, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class PostgresDatabase:
    def __init__(self) -> None:
        self._engine = create_async_engine(
            settings.postgres_url,
            echo=(settings.LOG_LEVEL == "DEBUG"),
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @property
    def engine(self):
        return self._engine


database = PostgresDatabase()
metadata = MetaData(schema=settings.POSTGRES_SCHEMA)


# Базовый класс для моделей
class Base(DeclarativeBase):
    metadata = metadata
    type_annotation_map = {
        str: String().with_variant(String(255), "postgresql"),
        Dict[str, Any]: JSON,
    }
