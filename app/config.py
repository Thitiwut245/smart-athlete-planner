from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()
class Settings(BaseModel):
    api_key: str = os.getenv("API_KEY", "dev-secret-key")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./smart.db")
settings = Settings()
