from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import chat, session, upload
from backend.database.database import Base, engine
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized")

    yield
    logger.info("Paperlens API shutdown")


app = FastAPI(
    title="Paperlens API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.get("/")
def root():
    """
    Root endpoint.
    """
    
    return {
        "message": "PaperLens API is running"
    }

app.include_router(session.router)
app.include_router(upload.router)
app.include_router(chat.router)