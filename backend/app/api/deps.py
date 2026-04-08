from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = request.app.state.session_maker
    async with async_session_maker() as session:
        yield session
