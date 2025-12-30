from typing import AsyncGenerator


from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# -------------------------------------------------
# Async Engine
# -------------------------------------------------
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """
    Creates the SQLAlchemy async engine.

    Pooling is enabled by default.
    In test environments, pooling can be disabled if needed.
    """
    return create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)


# -------------------------------------------------
# Initialization / Shutdown
# -------------------------------------------------
from app.db.base import Base

async def init_db() -> None:
    """
    Initializes database engine and session factory.
    Called once at application startup.
    """
    global _engine, _session_factory

    if _engine is not None:
        return

    logger.info("Initializing database engine")

    _engine = _create_engine()
    _session_factory = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Create tables for local/dev
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables ensured")




async def close_db() -> None:
    """
    Gracefully disposes database connections.
    Called once at application shutdown.
    """
    global _engine

    if _engine is not None:
        logger.info("Disposing database engine")
        await _engine.dispose()
        _engine = None


# -------------------------------------------------
# Session Dependency
# -------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional async database session.

    - Commits on success
    - Rolls back on exception
    - Always closes the session
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
