from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.database.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.crud.auth import register_user, login_user, get_user_by_email
from app.utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = await register_user(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=400, detail="User registration failed")

    # Генерация токена для нового пользователя
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return AuthResponse(userId=user.id, token=token)

@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await login_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Генерация токена при успешном входе
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return AuthResponse(userId=user.id, token=token)

