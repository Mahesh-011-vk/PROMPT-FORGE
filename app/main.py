"""
PromptForge AI - FastAPI Master Application.
"""

import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
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
    description=(
        f"Enterprise AI Prompt Engineering Platform. {__tagline__}\n\n"
        "### 🌟 [👉 CLICK HERE TO OPEN THE PROMPTFORGE INTERACTIVE WEB APPLICATION](/) 🌟\n\n"
        "*Full GUI with Prompt Studio, Optimizer, 7D Evaluation Lab, Multi-Agent Graph, Vector RAG & Analytics.*"
    ),
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


STATIC_INDEX_PATH = os.path.join(os.path.dirname(__file__), "ui", "static", "index.html")


def get_index_html() -> str:
    if os.path.exists(STATIC_INDEX_PATH):
        with open(STATIC_INDEX_PATH, encoding="utf-8") as f:
            return f.read()
    return "<h1>PromptForge AI</h1><p>Application is loading...</p>"


@app.get("/", tags=["Root"])
async def root(request: Request):
    """Platform root endpoint: serves the interactive UI to web browsers, or returns JSON for API clients."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept and "application/json" not in accept:
        return HTMLResponse(content=get_index_html())
    return ResponseEnvelope(
        data={
            "app": __app_name__,
            "version": __version__,
            "tagline": __tagline__,
            "ui": "/",
            "docs": "/docs",
            "api_v1": settings.API_V1_PREFIX,
        }
    )


@app.get("/app", tags=["Root"], response_class=HTMLResponse)
async def app_frontend():
    """Direct route for interactive web application."""
    return HTMLResponse(content=get_index_html())


@app.get("/studio", tags=["Root"], response_class=HTMLResponse)
async def studio_frontend():
    """Direct route for interactive web studio."""
    return HTMLResponse(content=get_index_html())


# Mount API v1 Master Router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

# Mount Interactive NiceGUI UI
from app.ui.app import mount_ui

mount_ui(app)
