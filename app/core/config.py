from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Required in .env
    LLM_PROVIDER: str
    LLM_URL: str
    LLM_NAME: str
    DB_PATH: str
    
    # Internal defaults
    MAX_PARALLEL_SCANS: int = 5
    SCAN_TTL_HOURS: int = 24
    PROJECT_NAME: str = "Code Review Platform POC"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
