from  sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

#SQLite Engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

logger.info("SQLite database engine initialized")

#Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

#Base class for all database models
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    logger.info("Database session opened")
    try:
        yield db
    finally:
        db.close()
        logger.info("Database session closed")