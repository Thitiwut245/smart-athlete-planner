from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import os

from .db import Base, engine
from .routers import auth_google, athletes, plans, sessions, exercise

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Athlete Planner (Boxing) — Bright & Sporty + Google Sign-In")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY","change-me"), session_cookie="sap_session", same_site="lax")

static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(static_path / "index.html")

app.include_router(auth_google.router)
app.include_router(athletes.router)
app.include_router(plans.router)
app.include_router(sessions.router)
app.include_router(exercise.router)

@app.get("/healthz")
def health(): return {"ok": True}
