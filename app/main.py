"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.api.routers import health, payments, merchants
from app.services.exceptions import PaymentGatewayException


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="Payment Gateway Simulator",
        description="Production-grade payment processing sandbox for testing and QA",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(PaymentGatewayException)
    async def payment_gateway_exception_handler(
        request: Request,
        exc: PaymentGatewayException,
    ) -> JSONResponse:
        """Handle payment gateway exceptions.

        Args:
            request: FastAPI request
            exc: Exception

        Returns:
            JSONResponse: Error response
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle validation errors.

        Args:
            request: FastAPI request
            exc: Exception

        Returns:
            JSONResponse: Error response
        """
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": "Validation failed",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )

    # Include routers
    app.include_router(health.router)
    app.include_router(payments.router, prefix="/api/v1")
    app.include_router(merchants.router, prefix="/api/v1")

    return app


app = create_app()
