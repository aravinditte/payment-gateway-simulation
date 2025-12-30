import hashlib
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.merchant import Merchant


class MerchantService:
    """
    Handles merchant-related operations.
    """

    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        raw_key = f"sk_test_{secrets.token_hex(24)}"
        hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return raw_key, hashed

    @classmethod
    async def create_merchant(
        cls,
        *,
        db: AsyncSession,
        name: str,
        email: str,
        webhook_url: str | None = None,
    ) -> tuple[Merchant, str]:
        raw_key, hashed_key = cls.generate_api_key()

        merchant = Merchant(
            name=name,
            email=email,
            api_key_hash=hashed_key,
            webhook_secret=secrets.token_hex(32),
            webhook_url=webhook_url,
        )

        db.add(merchant)
        await db.flush()

        return merchant, raw_key
