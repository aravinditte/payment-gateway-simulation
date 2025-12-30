import hashlib
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.merchant import Merchant


class MerchantRepository:
    """
    Data access layer for Merchant entities.
    """

    @staticmethod
    def _hash_api_key(api_key: str) -> str:
        """
        Hashes API key using SHA-256 before lookup.
        """
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    @classmethod
    async def get_by_api_key(
        cls,
        db: AsyncSession,
        api_key: str,
    ) -> Optional[Merchant]:
        """
        Retrieves merchant by hashed API key.
        """
        api_key_hash = cls._hash_api_key(api_key)

        stmt = select(Merchant).where(
            Merchant.api_key_hash == api_key_hash
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        merchant_id,
    ) -> Optional[Merchant]:
        stmt = select(Merchant).where(Merchant.id == merchant_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
