"""
PromptForge AI - FastAPI Master Application.
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __app_name__, __tagline__, __version__
from app.api.v1.router import api_v1_router
from app.config.settings import settings
from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.exceptions import PromptForgeException
from app.core.logging import logger
from app.core.seeder import seed_defaults
from app.schemas.common import ErrorDetail, ResponseEnvelope, ResponseMeta


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and graceful shutdown."""
    logger.info(f"Starting {__app_name__} v{__version__}...")
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
    logger.info(f"{__app_name__} initialized successfully.")
    yield
    logger.info(f"Shutting down {__app_name__}...")
    await close_db()


app = FastAPI(
    title=__app_name__,
    version=__version__,
    description=f"Enterprise AI Prompt Engineering Platform. {__tagline__}",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def context_and_timing_middleware(request: Request, call_next):
    """Injects correlation request ID and calculates request latency."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# Exception Handlers
@app.exception_handler(PromptForgeException)
async def promptforge_exception_handler(request: Request, exc: PromptForgeException):
    """Handles domain-specific PromptForge exceptions."""
    request_id = getattr(request.state, "request_id", None)
    logger.warning(f"Domain exception: {exc.code} - {exc.message}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseEnvelope(
            success=False,
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                request_id=request_id,
                details=exc.details,
            ),
            meta=ResponseMeta(request_id=request_id),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic request validation errors."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseEnvelope(
            success=False,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Request payload failed schema validation.",
                request_id=request_id,
                details={"errors": exc.errors()},
            ),
            meta=ResponseMeta(request_id=request_id),
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles standard HTTP exceptions (e.g. 404, 405)."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseEnvelope(
            success=False,
            error=ErrorDetail(
                code=f"HTTP_{exc.status_code}",
                message=str(exc.detail),
                request_id=request_id,
            ),
            meta=ResponseMeta(request_id=request_id),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches unhandled server errors and shields internal traces from users."""
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled server exception: {exc}", exc_info=True, extra={"request_id": request_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseEnvelope(
            success=False,
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred. Please contact support with the request ID.",
                request_id=request_id,
            ),
            meta=ResponseMeta(request_id=request_id),
        ).model_dump(),
    )


# Root & Health Endpoints
@app.get("/health", tags=["Health"])
async def root_health():
    """Top-level health check endpoint."""
    return ResponseEnvelope(
        data={
            "status": "healthy",
            "app": __app_name__,
            "version": __version__,
            "environment": settings.ENVIRONMENT,
            "demo_mode": settings.DEMO_MODE,
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Platform root information and documentation navigation."""
    return ResponseEnvelope(
        data={
            "app": __app_name__,
            "version": __version__,
            "tagline": __tagline__,
            "docs": "/docs",
            "api_v1": settings.API_V1_PREFIX,
        }
    )


# Mount API v1 Master Router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
