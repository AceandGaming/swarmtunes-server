import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.v1.server import v1_router
from automated.cleanup import clear_temp
from automated.tasks import sync_task, update_albums_task
from core.log import setup_logging
from database.database import create

app = FastAPI(
    title="SwarmTunes API",
    version="2.0.0-beta",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["swarmtunes.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/v1")


@app.on_event("startup")
async def startup():
    clear_temp()
    setup_logging()
    create()
    update_albums_task()
    # asyncio.create_task(asyncio.to_thread(sync_task))  # temp


@app.get("/")
async def root():
    return RedirectResponse(url="/v1")
