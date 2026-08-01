import re

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from database.dependencies import get_db
from features.playlist import create_playlist_service
from features.user import UserRoles, to_network_v2
from general.auth import AuthManager
from general.ip import SignupLimit

from .shared import APIException, auth_required, get_ip

auth_router = APIRouter()

signup_limit = SignupLimit()


def validate_username(username: str):
    username = username.strip().lower()
    username = re.sub(r"\s+", " ", username)

    if len(username) > 32:
        raise APIException("USERNAME_TOO_SHORT", "Username is too long")
    elif len(username) < 3:
        raise APIException("USERNAME_TOO_SHORT", "Username is too short")
    if not re.match(r"^[a-z0-9_-]+$", username):
        raise APIException("INVALID_USERNAME", "Invalid username characters")

    return username


def validate_password(password: str, strict=False):
    if len(password) > 256:
        raise APIException("PASSWORD_TOO_LONG", "Password is too long")
    if len(password) <= (8 if strict else 0):
        raise APIException("PASSWORD_TOO_SHORT", "Password is too short")

    if strict:
        if password.lower().startswith("password"):
            raise APIException(
                "PASSWORD_TOO_WEAK", "Please use a less common password"
            )
        if not re.search(r"[0-9]", password):
            raise APIException(
                "PASSWORD_TOO_WEAK", "Password must contain a number"
            )

    return password


class LoginRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/login")
def login(
    req: LoginRequest,
    response: Response,
    db=Depends(get_db),
):
    auth = AuthManager(db)
    playlist_service = create_playlist_service(db)

    username = validate_username(req.username)
    password = validate_password(req.password)

    identity = auth.login_legacy(username, password)
    if not identity:
        raise APIException(
            "INVALID_USERNAME_OR_PASSWORD",
            "Invalid username or password",
            status_code=401,
        )

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

    return to_network_v2(identity.user)


@auth_router.post("/users")
def signup(
    req: LoginRequest,
    response: Response,
    db=Depends(get_db),
    ip=Depends(get_ip),
):
    auth = AuthManager(db)
    playlist_service = create_playlist_service(db)

    username = validate_username(req.username)
    password = validate_password(req.password, True)

    if not signup_limit.can_signup(ip):
        raise APIException(
            "ACCOUNT_LIMIT_REACHED",
            "Account limit reached",
            status_code=429,
        )

    identity = auth.signup_legacy(username, password)
    if not identity:
        raise APIException(
            "INVALID_USERNAME_OR_PASSWORD",
            "Invalid username or password",
            status_code=401,
        )

    signup_limit.on_signup(ip)

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

    return to_network_v2(identity.user)


@auth_router.post("/logout")
def logout(
    response: Response, token=Depends(auth_required), db=Depends(get_db)
):
    db.delete(token)

    response.delete_cookie(
        key="sessionToken",
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth_router.get("/me")
def get_self(token=Depends(auth_required)):
    return to_network_v2(token.user)
