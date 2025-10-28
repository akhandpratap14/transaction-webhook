# app/database.py
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import Boolean, DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.config import settings

# ✅ Build full DB URL
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# Optional schema
metadata = MetaData(schema=settings.DB_SCHEMA)


class BaseModel(DeclarativeBase):
    __abstract__ = True
    metadata = metadata

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


# ✅ Async SQLAlchemy engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=40,
    max_overflow=20,
    pool_recycle=3600,
    isolation_level="AUTOCOMMIT",
)

# ✅ Async session maker
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ✅ Dependency for FastAPI routes
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
