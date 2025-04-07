from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.email import send_reset_email
from fastapi import HTTPException

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Функция для получения пользователя по email
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

# Функция для регистрации нового пользователя
async def register_user(db: AsyncSession, email: str, password: str):
    # Проверка, существует ли уже пользователь с таким email
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        return None  # Email уже зарегистрирован

    # Хеширование пароля
    hashed_pw = hash_password(password)
    # Создание нового пользователя
    new_user = User(email=email, password_hash=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Возвращаем объект пользователя
    return new_user

# Функция для входа пользователя
async def login_user(db: AsyncSession, email: str, password: str):
    # Получаем пользователя по email
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None  # Неверные данные для входа

    # Возвращаем объект пользователя
    return user

async def recover_password(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерируем фейковую ссылку для восстановления (в реальности тут был бы токен)
    reset_link = f"http://localhost:8000/reset-password/{user.id}"

    # Отправляем письмо
    send_reset_email(email, reset_link)

    return {"message": "Reset link sent"}
