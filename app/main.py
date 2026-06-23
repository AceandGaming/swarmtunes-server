import core.paths
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from api.v1.server import v1_router
from database.database import create

app = FastAPI()
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
    create()

@app.get("/")
async def root():
    return RedirectResponse(url="/v1")
