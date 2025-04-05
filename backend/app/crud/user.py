from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_pw
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
