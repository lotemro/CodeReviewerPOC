from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Code Review Platform POC"
    DEBUG: bool = False
    
    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # Options: "ollama", "mock" (can add "openai" later)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Database Settings
    DB_PATH: str = "code_review.db"
    
    # Concurrency Settings
    MAX_PARALLEL_SCANS: int = 5
    
    # TTL Settings (in hours)
    SCAN_TTL_HOURS: int = 24
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
