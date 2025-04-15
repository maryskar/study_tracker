import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.email import send_reset_email
from fastapi import HTTPException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.database.database import get_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Настройки токена
SECRET_KEY = "supersecretkey"  #такой же, как в utils/security.py
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))

        if user_id is None:
            logger.error("Invalid token: user_id is None")
            raise credentials_exception
        logger.info(f"Token successfully decoded. User ID: {user_id}")
    except (JWTError, ValueError, TypeError) as e:
        logger.error(f"Error decoding token or invalid user_id: {e}")
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        logger.error(f"User with ID {user_id} not found in the database")
        raise credentials_exception

    logger.info(f"User {user_id} authenticated successfully.")
    return user
