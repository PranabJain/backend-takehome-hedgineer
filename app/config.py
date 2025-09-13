import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    database_path: str = os.getenv("DATABASE_PATH", "/data/index.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis_enabled: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    index_base_level: float = float(os.getenv("INDEX_BASE_LEVEL", "100.0"))


settings = Settings()

