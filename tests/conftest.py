"""Pytest configuration and fixtures."""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Merchant, APIKey
from app.core.security import generate_api_key, generate_webhook_secret


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    yield async_session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_merchant(test_db):
    """Create test merchant."""
    async with test_db() as session:
        merchant = Merchant(
            id=str(uuid.uuid4()),
            name="Test Merchant",
            email="test@merchant.com",
            webhook_url="https://webhook.test.com",
            webhook_secret=generate_webhook_secret(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(merchant)
        await session.flush()

        api_key, api_secret = generate_api_key()
        db_api_key = APIKey(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            api_key=api_key,
            api_secret=api_secret,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        session.add(db_api_key)
        await session.commit()

        yield {
            "merchant": merchant,
            "api_key": api_key,
            "api_secret": api_secret,
        }
