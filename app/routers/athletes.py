from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal, Base, engine
from ..models import Athlete, User
from ..deps import get_current_user, get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/athletes", tags=["athletes"])
Base.metadata.create_all(bind=engine)

class AthleteCreate(BaseModel):
    name: str
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    stance: Optional[str] = None
    level: Optional[str] = "beginner"
    weekly_availability: int = 4
    goal: Optional[str] = "general_skill"

class AthleteOut(BaseModel):
    id: int
    name: str
    level: Optional[str] = None
    weekly_availability: int
    goal: Optional[str] = None
    class Config: from_attributes = True

@router.post("", response_model=AthleteOut)
def create_athlete(payload: AthleteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = Athlete(user_id=user.id, **payload.dict())
    db.add(a); db.commit(); db.refresh(a); return a

@router.get("", response_model=list[AthleteOut])
def list_athletes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Athlete).filter(Athlete.user_id==user.id).all()

@router.delete("/{athlete_id}")
def delete_athlete(athlete_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Athlete).filter(Athlete.id==athlete_id, Athlete.user_id==user.id).first()
    if not a: raise HTTPException(404, "Athlete not found")
    db.delete(a); db.commit(); return {"ok": True}
