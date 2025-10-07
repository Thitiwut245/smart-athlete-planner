from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from ..db import SessionLocal, Base, engine
from ..models import Session as SessionModel, Athlete, User
from ..deps import get_current_user, get_db
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])
Base.metadata.create_all(bind=engine)

class SessionCreate(BaseModel):
    athlete_id: int
    plan_id: Optional[int] = None
    date: date
    type: str
    rounds: int = 0
    minutes: int = 0
    rpe: Optional[float] = None
    notes: Optional[str] = None

class SessionOut(SessionCreate):
    id: int
    class Config: from_attributes = True

@router.post("", response_model=SessionOut)
def create_session(payload: SessionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ath = db.query(Athlete).filter(Athlete.id==payload.athlete_id, Athlete.user_id==user.id).first()
    if not ath: raise HTTPException(404, "Athlete not found")
    s = SessionModel(user_id=user.id, **payload.dict())
    db.add(s); db.commit(); db.refresh(s); return s

@router.get("/athlete/{athlete_id}", response_model=List[SessionOut])
def list_sessions(athlete_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user), from_date: date | None = Query(default=None, alias="from"), to: date | None = None):
    q = db.query(SessionModel).filter(SessionModel.athlete_id==athlete_id, SessionModel.user_id==user.id)
    if from_date: q = q.filter(SessionModel.date >= from_date)
    if to: q = q.filter(SessionModel.date <= to)
    return q.order_by(SessionModel.date.desc()).all()
