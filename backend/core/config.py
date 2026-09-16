import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    MODEL_NAME: str = "gemini-3.5-flash"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "10"))


settings = Settings()
