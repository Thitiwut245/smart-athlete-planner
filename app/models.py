from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    athletes = relationship("Athlete", back_populates="owner", cascade="all,delete")

class Athlete(Base):
    __tablename__ = "athletes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    stance = Column(String)
    level = Column(String)
    weekly_availability = Column(Integer, default=4)
    goal = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="athletes")
    plans = relationship("Plan", back_populates="athlete", cascade="all,delete")
    sessions = relationship("Session", back_populates="athlete", cascade="all,delete")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    start_date = Column(Date)
    weeks = Column(Integer, default=6)
    microcycles = Column(Text)
    intensity_tgt = Column(Float, default=1.0)
    notes = Column(Text)

    athlete = relationship("Athlete", back_populates="plans")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    date = Column(Date)
    type = Column(String)
    rounds = Column(Integer, default=0)
    minutes = Column(Integer, default=0)
    rpe = Column(Float)
    hr_avg = Column(Integer)
    hr_max = Column(Integer)
    punches_thrown = Column(Integer)
    soreness = Column(Integer)
    sleep_hours = Column(Float)
    notes = Column(Text)

    athlete = relationship("Athlete", back_populates="sessions")
