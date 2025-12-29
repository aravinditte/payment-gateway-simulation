"""Authentication service."""

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import APIKey, Merchant
from app.services.exceptions import AuthenticationError
from app.services.merchant_service import MerchantService


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session
        """
        self.merchant_service = MerchantService(session)

    async def authenticate_request(
        self, authorization: str
    ) -> tuple[Merchant, APIKey]:
        """Authenticate API request.

        Args:
            authorization: Authorization header value

        Returns:
            tuple[Merchant, APIKey]: (merchant, api_key_record)

        Raises:
            AuthenticationError: If authentication fails
        """
        if not authorization:
            raise AuthenticationError("Missing authorization header")

        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationError("Invalid authorization header format")

        api_key = parts[1]

        try:
            merchant, api_key_record = await self.merchant_service.authenticate(api_key)
            return merchant, api_key_record
        except Exception as e:
            raise AuthenticationError(str(e))
