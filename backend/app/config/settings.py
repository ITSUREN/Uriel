# backend/app/config/settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_path: str = "./backend/app/data/uriel.db"
    data_dir: str = "./data/documents"
    default_algorithm: str = "bm25"
    auto_index_on_startup: bool = True
    allowed_root: str | None = None

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()