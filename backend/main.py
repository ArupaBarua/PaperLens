from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

templates = Jinja2Templates(
    directory="backend/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="backend/static"),
    name="static"
)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Returns the main PaperLens web page.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

app.include_router(session.router)
app.include_router(upload.router)
app.include_router(chat.router)