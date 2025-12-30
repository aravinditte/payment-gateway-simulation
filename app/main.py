from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import AppException
from app.api.v1 import payments, refunds, webhooks, merchants
from app.db.session import init_db, close_db

settings = get_settings()
logger = get_logger(__name__)


# ---------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    setup_logging()
    logger.info("Starting Payment Gateway Simulator")

    await init_db()

    yield

    logger.info("Shutting down Payment Gateway Simulator")
    await close_db()


# ---------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------
app = FastAPI(
    title="Payment Gateway Simulator",
    description=(
        "A sandbox payment gateway for simulating payment flows, "
        "webhooks, failures, and retries. Designed for QA and developer testing."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

# CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    Adds request ID and measures latency.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()

    response = await call_next(request)

    duration_ms = int((time.time() - start_time) * 1000)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = str(duration_ms)

    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    return response


# ---------------------------------------------------------
# Exception Handling
# ---------------------------------------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handles domain-level application exceptions.
    """
    logger.warning(
        "application_error",
        extra={
            "path": request.url.path,
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Handles unexpected system errors.
    """
    logger.exception("unhandled_exception", extra={"path": request.url.path})

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            }
        },
    )


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------
app.include_router(
    merchants.router,
    prefix="/api/v1/merchants",
    tags=["Merchants"],
)

app.include_router(
    payments.router,
    prefix="/api/v1/payments",
    tags=["Payments"],
)

app.include_router(
    refunds.router,
    prefix="/api/v1/refunds",
    tags=["Refunds"],
)

app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["Webhooks"],
)


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {
        "status": "ok",
        "service": "payment-gateway-simulator",
        "version": app.version,
    }
