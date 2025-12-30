from fastapi import APIRouter, Request, Header

from app.core.security import verify_webhook_signature
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/receive")
async def receive_webhook(
    request: Request,
    x_signature: str = Header(None, alias=settings.WEBHOOK_SIGNATURE_HEADER),
):
    """
    Endpoint for merchants to test webhook signature verification.
    """
    raw_body = await request.body()

    verify_webhook_signature(
        payload=raw_body,
        signature_header=x_signature,
        secret=settings.SECRET_KEY,
        tolerance_seconds=settings.WEBHOOK_TOLERANCE_SECONDS,
    )

    return {"status": "verified"}
