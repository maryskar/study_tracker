from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user
from app.database.database import get_db

router = APIRouter()

@router.get("/users/", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.post("/users/", response_model=UserOut)
async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db=db, user=user)
