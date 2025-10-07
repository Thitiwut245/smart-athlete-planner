from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import User
from .security import decode_token

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split(" ", 1)[1]
    sub = decode_token(token)
    if not sub:
        raise HTTPException(401, "Invalid or expired token")
    u = db.query(User).get(int(sub))
    if not u:
        raise HTTPException(401, "User not found")
    return u
