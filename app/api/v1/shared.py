from fastapi import Depends, HTTPException, Response, Cookie
from database.dependencies import get_db
from general.auth import AuthManager
from uuid import UUID

def auth_required(sessionToken: str = Cookie(None), db = Depends(get_db)):
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