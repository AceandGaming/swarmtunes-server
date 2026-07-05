import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.v1.server import v1_router
from automated.cleanup import clear_temp
from core.log import setup_logging
from core.scheduler import start_automated_tasks
from database.database import create as create_db
from external.emotes import load_emotes


@asynccontextmanager
async def lifespan(app: FastAPI):
    clear_temp()
    setup_logging()
    create_db()
    load_emotes()

    scheduler = start_automated_tasks()
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="SwarmTunes API",
    version="2.0.0-beta",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://swarmtunes.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/v1")


@app.get("/")
async def root():
    return RedirectResponse(url="/v1")
