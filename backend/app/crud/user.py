from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_user(db: AsyncSession, user: UserCreate):
    new_user = User(username=user.username, hashed_password=user.hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
