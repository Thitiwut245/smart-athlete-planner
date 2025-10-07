from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
import json
from ..db import SessionLocal, Base, engine
from ..models import Athlete, Plan, User
from ..deps import get_current_user, get_db
from ..services.planner import generate_microcycles
from pydantic import BaseModel
from typing import Optional, Any, List

router = APIRouter(prefix="/api/v1/plans", tags=["plans"])
Base.metadata.create_all(bind=engine)

class PlanOut(BaseModel):
    id: int
    athlete_id: int
    start_date: Optional[date]
    weeks: int
    microcycles: Any
    intensity_tgt: float
    notes: Optional[str] = None
    class Config: from_attributes = True

@router.post("/generate", response_model=PlanOut)
def generate_plan(athlete_id: int = Query(...), weeks: int = Query(6, ge=4, le=12), start: date | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    athlete = db.query(Athlete).filter(Athlete.id==athlete_id, Athlete.user_id==user.id).first()
    if not athlete: raise HTTPException(404, "Athlete not found")
    start_date = start or date.today()
    micro = generate_microcycles(start_date, weeks, athlete.weekly_availability, athlete.goal or "general_skill", athlete.level or "beginner")
    plan = Plan(user_id=user.id, athlete_id=athlete.id, start_date=start_date, weeks=weeks,
        microcycles=json.dumps([{**d, "date": d["date"].isoformat()} for d in micro]), intensity_tgt=1.0)
    db.add(plan); db.commit(); db.refresh(plan); return plan

@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.query(Plan).filter(Plan.id==plan_id, Plan.user_id==user.id).first()
    if not p: raise HTTPException(404, "Plan not found")
    return p

@router.get("/athlete/{athlete_id}", response_model=List[PlanOut])
def list_plans(athlete_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Plan).filter(Plan.athlete_id==athlete_id, Plan.user_id==user.id).all()
