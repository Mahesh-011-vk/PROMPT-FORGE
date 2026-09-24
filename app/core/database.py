"""
PromptForge AI - Database Connection and Session Lifecycle.

Configures asynchronous SQLAlchemy engine, session factory, table creation,
and FastAPI dependency injection.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings
from app.core.logging import logger
from app.models.base import Base

# Engine configuration with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ECHO_SQL,
    future=True,
    # SQLite requires check_same_thread=False for async connection
    connect_args={"check_same_thread": False} if settings.is_sqlite else {},
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async_session_factory = AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes tables in database on application startup."""
    logger.info("Initializing database schemas...", extra={"db_url": settings.DATABASE_URL})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas initialized successfully.")


async def close_db() -> None:
    """Disposes database connection pool cleanly on shutdown."""
    logger.info("Closing database engine pool...")
    await engine.dispose()
    logger.info("Database engine pool closed.")
