from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Audio Analytics MVP"

    # Настройки базы данных
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/audio_analytics"

    # Настройки Redis для очередей Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # Настройки S3 (MinIO) для хранения аудиофайлов
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "admin"
    S3_SECRET_KEY: str = "password123"
    S3_BUCKET_NAME: str = "audio-records"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()