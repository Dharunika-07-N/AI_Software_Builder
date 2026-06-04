import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # If no API key is set, we default to MOCK_MODE = True
    # The user can override this by explicitly setting MOCK_MODE=False in env
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() in ("true", "1", "yes")
    
    # SQLite DB for dynamic execution runtime
    RUNTIME_DB_PATH: str = os.getenv("RUNTIME_DB_PATH", "runtime.db")
    
    @property
    def has_llm_credentials(self) -> bool:
        return bool(self.OPENAI_API_KEY or self.GEMINI_API_KEY)

settings = Settings()
# If we have credentials, check if we should disable mock mode
if settings.has_llm_credentials and os.getenv("MOCK_MODE") is None:
    settings.MOCK_MODE = False
