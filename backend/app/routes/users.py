from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.models.user import User
from sqlalchemy.future import select

from sqlalchemy.orm import Session
from app.crud.user import create_user
from app.database.database import SessionLocal

from app.database.database import get_db

router = APIRouter()

from app.schemas.user import UserCreate

@router.post("/users/")
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, username=user.username, hashed_password=user.hashed_password)
