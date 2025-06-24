import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql+asyncpg://admin:password@db:5432/eduportal'
)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# PUBLIC_INTERFACE
async def get_db():
    """Yields an async DB session for FastAPI endpoints, closes when done."""
    async with async_session() as session:
        yield session
