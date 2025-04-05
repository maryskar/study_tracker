from fastapi import FastAPI
from app.routes import users, auth
from app.database.database import create_tables
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Pomodoro API", version="1.0.0")

# Этот маршрут генерирует OpenAPI схему
@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return get_openapi(
        title="Pomodoro API",
        version="1.0.0",
        routes=app.routes,
    )

# Подключение роутеров
app.include_router(users.router)
app.include_router(auth.router)

# Создание таблиц при запуске приложения
@app.on_event("startup")
async def startup():
    await create_tables()
