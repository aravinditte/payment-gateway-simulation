"""Merchant service for merchant operations."""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key, generate_webhook_secret
from app.db.models import APIKey, Merchant
from app.repositories.api_key_repository import APIKeyRepository
from app.repositories.merchant_repository import MerchantRepository
from app.services.exceptions import NotFoundError, ValidationError


class MerchantService:
    """Service for merchant operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session
        """
        self.merchant_repo = MerchantRepository(session)
        self.api_key_repo = APIKeyRepository(session)
        self.session = session

    async def create_merchant(
        self, name: str, email: str, webhook_url: Optional[str] = None
    ) -> Merchant:
        """Create new merchant.

        Args:
            name: Merchant name
            email: Merchant email
            webhook_url: Optional webhook URL

        Returns:
            Merchant: Created merchant

        Raises:
            ValidationError: If email already exists
        """
        existing = await self.merchant_repo.get_by_email(email)
        if existing:
            raise ValidationError(f"Merchant with email {email} already exists")

        merchant = await self.merchant_repo.create(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            webhook_url=webhook_url,
            webhook_secret=generate_webhook_secret() if webhook_url else None,
        )
        await self.merchant_repo.commit()
        return merchant

    async def get_merchant(self, merchant_id: str) -> Merchant:
        """Get merchant by ID.

        Args:
            merchant_id: Merchant ID

        Returns:
            Merchant: Merchant

        Raises:
            NotFoundError: If merchant not found
        """
        merchant = await self.merchant_repo.get_by_id(merchant_id)
        if not merchant:
            raise NotFoundError(f"Merchant {merchant_id} not found")
        return merchant

    async def generate_api_key(self, merchant_id: str) -> tuple[str, str]:
        """Generate new API key for merchant.

        Args:
            merchant_id: Merchant ID

        Returns:
            tuple[str, str]: (api_key, api_secret)

        Raises:
            NotFoundError: If merchant not found
        """
        merchant = await self.get_merchant(merchant_id)
        if not merchant:
            raise NotFoundError(f"Merchant {merchant_id} not found")

        api_key, api_secret = generate_api_key()

        db_api_key = await self.api_key_repo.create(
            id=str(uuid.uuid4()),
            merchant_id=merchant_id,
            api_key=api_key,
            api_secret=api_secret,
        )
        await self.api_key_repo.commit()

        return api_key, api_secret

    async def authenticate(self, api_key: str) -> tuple[Merchant, APIKey]:
        """Authenticate merchant by API key.

        Args:
            api_key: API key

        Returns:
            tuple[Merchant, APIKey]: (merchant, api_key_record)

        Raises:
            ValidationError: If API key is invalid
        """
        api_key_record = await self.api_key_repo.get_by_api_key(api_key)
        if not api_key_record:
            raise ValidationError("Invalid API key")

        merchant = await self.merchant_repo.get_by_id(api_key_record.merchant_id)
        if not merchant or not merchant.is_active:
            raise ValidationError("Merchant is not active")

        return merchant, api_key_record
