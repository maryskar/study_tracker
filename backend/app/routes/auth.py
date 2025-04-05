from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.crud.auth import register_user, login_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await register_user(db, data.email, data.password)
    if not result:
        raise HTTPException(status_code=400, detail="User already exists")
    return result

@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await login_user(db, data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result
