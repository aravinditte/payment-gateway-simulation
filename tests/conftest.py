import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import init_db, close_db, get_db_session


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Initialize and teardown database once per test session.
    """
    await init_db()
    yield
    await close_db()


@pytest.fixture
async def db_session() -> AsyncSession:
    """
    Provides a transactional DB session for tests.
    Rolls back after each test.
    """
    async for session in get_db_session():
        yield session
        await session.rollback()
