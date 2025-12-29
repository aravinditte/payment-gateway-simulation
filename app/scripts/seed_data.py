"""Seed database with demo merchants and API keys."""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.models import APIKey, Merchant
from app.core.security import generate_api_key, generate_webhook_secret


async def seed_merchants() -> None:
    """Seed demo merchants."""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async with async_session_maker() as session:
        # Check if merchants already exist
        from sqlalchemy import select
        result = await session.execute(select(Merchant))
        existing = result.scalars().first()
        if existing:
            print("Demo merchants already exist. Skipping seed.")
            await engine.dispose()
            return

        # Create demo merchants
        merchants = [
            {
                "id": str(uuid.uuid4()),
                "name": "Acme Corp",
                "email": "payments@acme.com",
                "webhook_url": "https://api.acme.com/webhooks/payments",
                "webhook_secret": generate_webhook_secret(),
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Tech Startup",
                "email": "billing@techstartup.io",
                "webhook_url": "https://webhook.techstartup.io/payments",
                "webhook_secret": generate_webhook_secret(),
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "E-commerce Store",
                "email": "ops@ecommerce.shop",
                "webhook_url": None,
                "webhook_secret": None,
                "is_active": True,
            },
        ]

        for merchant_data in merchants:
            merchant = Merchant(**merchant_data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            session.add(merchant)
            await session.flush()

            # Generate API key for each merchant
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

            print(f"\n✓ Created merchant: {merchant.name}")
            print(f"  Email: {merchant.email}")
            print(f"  API Key: {api_key}")
            print(f"  API Secret: {api_secret}")
            print(f"  Webhook URL: {merchant.webhook_url or 'Not configured'}")

        await session.commit()
        print("\n✓ Demo merchants seeded successfully!")

        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_merchants())
