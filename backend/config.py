from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Keys
    OPENROUTER_API_KEY: str
    OPENAI_API_KEY: str

    # Models
    LLM_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    VISION_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"

    # Database
    DATABASE_URL: str = "sqlite:///data/chat.db"

    # Vector Database
    CHROMA_DB_PATH: str = "data/chroma_db"

    # Data Directories
    UPLOAD_DIR: str = "data/uploaded_papers"
    IMAGE_DIR: str = "data/extracted_images"
    TABLE_DIR: str = "data/extracted_tables"

    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 10

    MEMORY_TRIGGER: int = 50
    MESSAGES_TO_SUMMARIZE: int = 30
    RECENT_MESSAGE_LIMIT: int = 20

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()