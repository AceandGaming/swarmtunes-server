import logging
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request

from database.dependencies import get_db
from general.auth import AuthManager

log = logging.getLogger()


def auth_required(sessionToken: str = Cookie(None), db=Depends(get_db)):
    auth = AuthManager(db)
    if not sessionToken:
        log.info("User failed to authenticate: Missing session token")
        raise HTTPException(401, detail="Unauthorized")

    try:
        id, secret = sessionToken.split(":")
        id = UUID(id)
    except ValueError:
        log.info("User failed to authenticate: Malformed session token")
        raise HTTPException(401, detail="Unauthorized")

    token = auth.verify_token(id, secret)
    if not token:
        log.info("User failed to authenticate: Invalid session token")
        raise HTTPException(401, detail="Unauthorized")

    return token


def get_ip(request: Request):
    if request.client is None:
        raise RuntimeError("No client address available")

    return request.client.host
