from fastapi import FastAPI
from app.routes import users
from app.database.database import create_tables

app = FastAPI()

# Подключение роутеров
app.include_router(users.router)

# Создание таблиц при запуске приложения
@app.on_event("startup")
async def startup():
    await create_tables()
