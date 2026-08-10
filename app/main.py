from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.v1.server import v1_router
from api.v2.server import v2_router
from api.v2.shared import APIException
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


class AddVaryOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        vary = response.headers.get("Vary")

        if not vary:
            response.headers["Vary"] = "Origin"

        return response


app = FastAPI(
    title="SwarmTunes API",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://swarmtunes.com"],
    allow_origin_regex=r"^https://[a-zA-Z0-9-]+\.swarmtunes-client\.pages\.dev$",  # Cloudflare Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AddVaryOriginMiddleware)


@app.exception_handler(APIException)
async def api_error_handler(
    request: Request,
    exc: APIException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors(),
            }
        },
    )


app.include_router(v1_router, prefix="/v1")
app.include_router(v2_router, prefix="/v2")


@app.get("/")
async def root():
    return RedirectResponse(url="/v1")
