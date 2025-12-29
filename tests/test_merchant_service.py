"""Tests for merchant service."""

import pytest

from app.db.models import Merchant
from app.services.merchant_service import MerchantService
from app.services.exceptions import ValidationError, NotFoundError


@pytest.mark.asyncio
async def test_create_merchant_success(test_db):
    """Test successful merchant creation."""
    async with test_db() as session:
        service = MerchantService(session)

        merchant = await service.create_merchant(
            name="Test Merchant",
            email="test@merchant.com",
            webhook_url="https://webhook.test.com",
        )

        assert merchant.id
        assert merchant.name == "Test Merchant"
        assert merchant.email == "test@merchant.com"
        assert merchant.webhook_url == "https://webhook.test.com"
        assert merchant.webhook_secret is not None


@pytest.mark.asyncio
async def test_create_merchant_duplicate_email(test_db):
    """Test merchant creation with duplicate email."""
    async with test_db() as session:
        service = MerchantService(session)

        await service.create_merchant(
            name="Merchant 1",
            email="duplicate@test.com",
        )

        with pytest.raises(ValidationError):
            await service.create_merchant(
                name="Merchant 2",
                email="duplicate@test.com",
            )


@pytest.mark.asyncio
async def test_get_merchant_success(test_db, test_merchant):
    """Test getting merchant."""
    async with test_db() as session:
        service = MerchantService(session)
        merchant_data = test_merchant
        merchant = merchant_data["merchant"]

        fetched = await service.get_merchant(merchant.id)

        assert fetched.id == merchant.id
        assert fetched.name == merchant.name


@pytest.mark.asyncio
async def test_get_merchant_not_found(test_db):
    """Test getting non-existent merchant."""
    async with test_db() as session:
        service = MerchantService(session)

        with pytest.raises(NotFoundError):
            await service.get_merchant("nonexistent")


@pytest.mark.asyncio
async def test_generate_api_key(test_db, test_merchant):
    """Test API key generation."""
    async with test_db() as session:
        service = MerchantService(session)
        merchant_data = test_merchant
        merchant = merchant_data["merchant"]

        api_key, api_secret = await service.generate_api_key(merchant.id)

        assert api_key.startswith("pk_")
        assert len(api_secret) > 10
