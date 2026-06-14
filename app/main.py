from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.v1.server import v1_router
import database.models #init db

app = FastAPI()
app.include_router(v1_router, prefix="/v1")

@app.get("/")
async def root():
    return RedirectResponse(url="/v1")