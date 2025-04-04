from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base  # импорт всех моделей
import os

# URL для подключения к PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:18092019@localhost/study_timer"
)

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронная фабрика сессий
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Асинхронный генератор сессии (используется через Depends)
async def get_db():
    async with SessionLocal() as session:
        yield session

# Функция создания таблиц при старте приложения
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# (опционально) Функция удаления таблиц
async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
