from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.utils.security import hash_password, verify_password, create_access_token

async def register_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar():
        return None  # Email уже существует
    new_user = User(email=email, password_hash=hash_password(password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    token = create_access_token({"sub": str(new_user.id)})
    return {"userId": new_user.id, "token": token}

async def login_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar()
    if not user or not verify_password(password, user.password_hash):
        return None
    token = create_access_token({"sub": str(user.id)})
    return {"userId": user.id, "token": token}
