from typing import AsyncGenerator, Annotated

from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from settings import settings


intpk = Annotated[int, mapped_column(primary_key=True, index=True)]


class Base(DeclarativeBase):
    pass


DB_URL = settings.get_db_url()
engine = create_async_engine(url=DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker.begin() as session:
        yield session
