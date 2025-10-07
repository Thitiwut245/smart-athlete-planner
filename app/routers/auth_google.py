from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import HTMLResponse
from authlib.integrations.starlette_client import OAuth
import os
from sqlalchemy.orm import Session
from ..db import SessionLocal, Base, engine
from ..models import User
from ..security import create_access_token

router = APIRouter(prefix="/auth/google", tags=["auth-google"])
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    client_kwargs={"scope": "openid email profile"},
)

REDIRECT_URL = os.getenv("OAUTH_REDIRECT_URL", "http://127.0.0.1:8000/auth/google/callback")

@router.get("/login", include_in_schema=False)
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, REDIRECT_URL, prompt="select_account")

@router.get("/callback", include_in_schema=False)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Google auth failed")

    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.google.parse_id_token(request, token)

    if not userinfo or "email" not in userinfo:
        raise HTTPException(status_code=401, detail="Google did not return email")

    email = userinfo["email"].lower()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user); db.commit(); db.refresh(user)

    jwt_token = create_access_token(str(user.id))

    html = f"""
    <html><body>
      <script>
        localStorage.setItem('sap_token', {jwt_token!r});
        window.location.replace('/#/dashboard');
      </script>
      Signing you in with Google…
    </body></html>
    """
    return HTMLResponse(content=html, status_code=200)
