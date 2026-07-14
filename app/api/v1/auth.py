import re

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from database.dependencies import get_db
from features.playlist import create_playlist_service
from features.user import UserRoles, to_network_v1
from general.auth import AuthManager
from general.ip import SignupLimit

from .shared import auth_required, get_ip

auth_router = APIRouter()

signup_limit = SignupLimit()


def validate_username(username: str):
    username = username.strip().lower()
    username = re.sub(r"\s+", " ", username)

    if len(username) > 32 or len(username) < 3:
        raise HTTPException(400, detail="Invalid username")
    if not re.match(r"^[a-z0-9_-]+$", username):
        raise HTTPException(400, detail="Invalid username")

    return username


def validate_password(password: str, strict=False):
    if len(password) > 256:
        raise HTTPException(400, detail="Password too long")
    if len(password) <= (8 if strict else 0):
        raise HTTPException(400, detail="Password too short")
    if strict:
        if password.lower().startswith("password"):
            raise HTTPException(400, detail="Password too common")
        if not re.search(r"[0-9]", password):
            raise HTTPException(400, detail="Password too weak")

    return password


class LoginRequest(BaseModel):
    username: str
    password: str
    create: bool = False
    remeber: bool = False


@auth_router.post("/users/login")
def login(
    req: LoginRequest,
    response: Response,
    db=Depends(get_db),
    ip=Depends(get_ip),
):
    auth = AuthManager(db)
    playlist_service = create_playlist_service(db)

    username = req.username
    password = req.password

    username = validate_username(username)

    if req.create:
        password = validate_password(password, True)

        if not signup_limit.can_signup(ip):
            raise HTTPException(429, detail="Account limit reached")

        identity = auth.signup_legacy(username, password)
        if not identity:
            raise HTTPException(400, detail="Invalid username")

        signup_limit.on_signup(ip)
    else:
        password = validate_password(password)

        identity = auth.login_legacy(username, password)
        if not identity:
            raise HTTPException(401, detail="Invalid username or password")

    playlist_service.ensure_liked_songs_playlist(identity.user)

    secret, token = auth.create_token(identity)
    db.flush()

    response.set_cookie(
        key="sessionToken",
        value=f"{token.id}:{secret}",
        max_age=int(token.maxAge),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return {
        "success": True,
        "isAdmin": identity.user.role == UserRoles.ADMIN,
        "id": identity.user.id,
        "username": identity.user.username,
    }


@auth_router.post("/me/logout")
def logout(token=Depends(auth_required), db=Depends(get_db)):
    db.delete(token)


@auth_router.get("/me/session")
def get_session(token=Depends(auth_required), db=Depends(get_db)):
    return {
        "success": True,
        "isAdmin": token.user.role == UserRoles.ADMIN,
        "id": token.user.id,
        "username": token.user.username,
    }


@auth_router.get("/me")
def get_self(token=Depends(auth_required)):
    return to_network_v1(token.user)
