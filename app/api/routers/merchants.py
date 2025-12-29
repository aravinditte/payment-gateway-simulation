"""Merchant endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.dependencies import get_current_merchant
from app.db.engine import get_db
from app.db.models import APIKey, Merchant
from app.services.exceptions import PaymentGatewayException
from app.services.merchant_service import MerchantService

router = APIRouter(prefix="/merchants", tags=["merchants"])


class CreateMerchantRequest(BaseModel):
    """Create merchant request."""

    name: str
    email: EmailStr
    webhook_url: Optional[str] = None


class MerchantResponse(BaseModel):
    """Merchant response."""

    id: str
    name: str
    email: str
    webhook_url: Optional[str] = None
    is_active: bool

    class Config:
        """Pydantic config."""

        from_attributes = True


class APIKeyResponse(BaseModel):
    """API key response."""

    api_key: str
    api_secret: str


@router.post("/", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def create_merchant(
    request: CreateMerchantRequest,
    session: AsyncSession = Depends(get_db),
) -> MerchantResponse:
    """Create new merchant.

    Args:
        request: Create merchant request
        session: Database session

    Returns:
        MerchantResponse: Created merchant

    Raises:
        HTTPException: If creation fails
    """
    service = MerchantService(session)

    try:
        merchant = await service.create_merchant(
            name=request.name,
            email=request.email,
            webhook_url=request.webhook_url,
        )
        return MerchantResponse.from_orm(merchant)
    except PaymentGatewayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/me", response_model=MerchantResponse)
async def get_current_merchant_info(
    merchant_data: tuple[Merchant, APIKey] = Depends(get_current_merchant),
) -> MerchantResponse:
    """Get current merchant info.

    Args:
        merchant_data: Current merchant

    Returns:
        MerchantResponse: Merchant details
    """
    merchant, _ = merchant_data
    return MerchantResponse.from_orm(merchant)


@router.post("/me/api-keys", response_model=APIKeyResponse)
async def generate_api_key(
    session: AsyncSession = Depends(get_db),
    merchant_data: tuple[Merchant, APIKey] = Depends(get_current_merchant),
) -> APIKeyResponse:
    """Generate new API key.

    Args:
        session: Database session
        merchant_data: Current merchant

    Returns:
        APIKeyResponse: New API key and secret

    Raises:
        HTTPException: If generation fails
    """
    merchant, _ = merchant_data
    service = MerchantService(session)

    try:
        api_key, api_secret = await service.generate_api_key(merchant.id)
        return APIKeyResponse(api_key=api_key, api_secret=api_secret)
    except PaymentGatewayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
