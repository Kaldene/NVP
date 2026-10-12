from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импорты роутеров
from app.api.v1.mobile import router as mobile_router
from app.api.v1.admin import router as admin_router

# Импорты для базы данных
from app.db.database import engine, Base

from app import models  # <--- Вот правильный импорт для твоей структуры!

from fastapi.staticfiles import StaticFiles
import os
# Генерируем таблицы (сработает при запуске, так как старую базу мы удалили)
from app.models import Dialog
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Audio Analytics MVP",
    description="Система аудиоаналитики для компьютерных клубов",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mobile_router, prefix="/api/v1/mobile", tags=["Mobile App"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Web Admin"])


os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/health")
async def health_check():
    return {"status": "ok"}