from datetime import timedelta
from typing import Any
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from database.dependencies import get_db
from features.session import Token
from features.user import UserRoles
from general.auth import AuthManager


class CachedJSONResponse(JSONResponse):
    def __init__(
        self,
        content,
        *,
        cache_for: timedelta,
        public: bool = True,
        imutable: bool = False,
        **kwargs,
    ):
        headers = kwargs.pop("headers", {})

        seconds = int(cache_for.total_seconds())

        visibility = "public" if public else "private"
        headers["Cache-Control"] = (
            f"{visibility}, max-age={seconds}, stale-while-revalidate={seconds / 10}"
        )
        if imutable:
            headers["Cache-Control"] += ", immutable"

        super().__init__(
            content=content,
            headers=headers,
            **kwargs,
        )


class APIException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Any | None = None,
    ):
        self.code = code.upper()
        self.message = message
        self.status_code = status_code
        self.details = details


class CachedResponse(JSONResponse):
    def __init__(self, response, **kwargs):
        super().__init__(response, **kwargs)
        self.headers["Cache-Control"] = "public, max-age=3600"


def auth_required(sessionToken: str = Cookie(None), db=Depends(get_db)):
    auth = AuthManager(db)
    if not sessionToken:
        raise HTTPException(401, detail="Unauthorized")

    try:
        id, secret = sessionToken.split(":")
        id = UUID(id)
    except ValueError:
        raise HTTPException(401, detail="Unauthorized")

    token = auth.verify_token(id, secret)
    if not token:
        raise HTTPException(401, detail="Unauthorized")

    return token


def get_ip(request: Request):
    if request.client is None:
        raise RuntimeError("No client address available")

    return request.client.host


def admin_required(token: Token = Depends(auth_required)):
    if token.user.role != UserRoles.ADMIN:
        raise HTTPException(403, detail="Forbidden")
    return token
