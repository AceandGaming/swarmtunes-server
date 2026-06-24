from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from database.dependencies import get_db
from features.user import UserRoles, to_network_v1
from pydantic import BaseModel
from general.auth import AuthManager
import re
from .shared import auth_required

auth_router = APIRouter()

def validate_username(username: str):
    username = username.strip()
    username = re.sub(r"\s+", " ", username)

    if len(username) > 32 or len(username) <= 3:
        raise HTTPException(400, detail="Invalid username")
    if not re.match(r"^[a-z0-9_-]+$", username):
        raise HTTPException(400, detail="Invalid username")

    return username

def validate_password(password: str, strict=False):
    if len(password) > 32 or len(password) <= (8 if strict else 0):
        raise HTTPException(400, detail="Invalid password")
    if strict:
        if password.lower().startswith("password"):
            raise HTTPException(400, detail="Password too weak")
        if not re.search(r"[0-9]", password):
            raise HTTPException(400, detail="Password too weak")

    return password



class LoginRequest(BaseModel):
    username: str
    password: str
    create: bool = False
    remeber: bool = False

@auth_router.post("/users/login")
def login(req: LoginRequest, response: Response, db = Depends(get_db)):
    auth = AuthManager(db)

    username = req.username
    password = req.password

    username = validate_username(username)
    
    if req.create:
        password = validate_password(password, True)

        identity = auth.signup_legacy(username, password)
        if not identity:
            raise HTTPException(400, detail="Invalid username")
    else:
        password = validate_password(password)

        identity = auth.login_legacy(username, password)
        if not identity:
            raise HTTPException(401, detail="Invalid username or password")

    secret, token = auth.create_token(identity)

    response.set_cookie(
        key="sessionToken",
        value=f"{token.id}:{secret}",
        max_age=int(token.maxAge),
        httponly=True,
        secure=True,
        samesite="lax"
    )

    return {
        "success": True, 
        "isAdmin": identity.user.role == UserRoles.ADMIN, 
        "id": identity.user.id, 
        "username": identity.user.username
    }

@auth_router.post("/me/logout")
def logout(token = Depends(auth_required), db = Depends(get_db)):
    db.delete(token)

@auth_router.get("/me/session")
def get_session(token = Depends(auth_required), db = Depends(get_db)):
    return {
        "success": True, 
        "isAdmin": token.user.role == UserRoles.ADMIN, 
        "id": token.user.id, 
        "username": token.user.username
    }

@auth_router.get("/me")
def get_self(token = Depends(auth_required)):
    return to_network_v1(token.user)