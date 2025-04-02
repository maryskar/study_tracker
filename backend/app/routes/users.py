from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.models.user import User
from sqlalchemy.future import select

from sqlalchemy.orm import Session
from app.crud.user import create_user
from app.database.database import SessionLocal

router = APIRouter()

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Роут для создания пользователя
@router.post("/users/")
def create_user_route(username: str, hashed_password: str, db: Session = Depends(get_db)):
    return create_user(db=db, username=username, hashed_password=hashed_password)
