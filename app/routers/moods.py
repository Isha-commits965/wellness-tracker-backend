from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import User, MoodEntry
from app.schemas import (
    MoodEntryCreate, MoodEntryUpdate, MoodEntry as MoodEntrySchema,
    MoodTrend
)
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=MoodEntrySchema)
async def create_mood_entry(
    mood_entry: MoodEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new mood entry"""
    # Check if entry already exists for this date
    existing_entry = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date == mood_entry.date
    ).first()
    
    if existing_entry:
        raise HTTPException(
            status_code=400,
            detail="Mood entry already exists for this date. Use PUT to update."
        )
    
    db_mood_entry = MoodEntry(
        user_id=current_user.id,
        date=mood_entry.date,
        mood_score=mood_entry.mood_score,
        energy_level=mood_entry.energy_level,
        stress_level=mood_entry.stress_level,
        notes=mood_entry.notes
    )
    
    db.add(db_mood_entry)
    db.commit()
    db.refresh(db_mood_entry)
    
    return db_mood_entry


@router.get("/", response_model=List[MoodEntrySchema])
async def get_mood_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mood entries with optional date filters"""
    query = db.query(MoodEntry).filter(MoodEntry.user_id == current_user.id)
    
    if start_date:
        query = query.filter(MoodEntry.date >= start_date)
    
    if end_date:
        query = query.filter(MoodEntry.date <= end_date)
    
    mood_entries = query.order_by(MoodEntry.date.desc()).all()
    
    return mood_entries


@router.get("/{entry_id}", response_model=MoodEntrySchema)
async def get_mood_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific mood entry"""
    mood_entry = db.query(MoodEntry).filter(
        MoodEntry.id == entry_id,
        MoodEntry.user_id == current_user.id
    ).first()
    
    if not mood_entry:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    
    return mood_entry


@router.put("/{entry_id}", response_model=MoodEntrySchema)
async def update_mood_entry(
    entry_id: int,
    mood_update: MoodEntryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a mood entry"""
    mood_entry = db.query(MoodEntry).filter(
        MoodEntry.id == entry_id,
        MoodEntry.user_id == current_user.id
    ).first()
    
    if not mood_entry:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    
    for field, value in mood_update.dict(exclude_unset=True).items():
        setattr(mood_entry, field, value)
    
    db.commit()
    db.refresh(mood_entry)
    
    return mood_entry


@router.delete("/{entry_id}")
async def delete_mood_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a mood entry"""
    mood_entry = db.query(MoodEntry).filter(
        MoodEntry.id == entry_id,
        MoodEntry.user_id == current_user.id
    ).first()
    
    if not mood_entry:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    
    db.delete(mood_entry)
    db.commit()
    
    return {"message": "Mood entry deleted successfully"}


@router.get("/trends/", response_model=List[MoodTrend])
async def get_mood_trends(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mood trends over a specified number of days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    mood_entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= start_date,
        MoodEntry.date <= end_date
    ).order_by(MoodEntry.date.asc()).all()
    
    trends = []
    for entry in mood_entries:
        trends.append(MoodTrend(
            date=entry.date,
            mood_score=float(entry.mood_score),
            energy_level=float(entry.energy_level) if entry.energy_level else None,
            stress_level=float(entry.stress_level) if entry.stress_level else None
        ))
    
    return trends


@router.get("/stats/weekly")
async def get_weekly_mood_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly mood statistics"""
    # Get last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    mood_entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= start_date,
        MoodEntry.date <= end_date
    ).all()
    
    if not mood_entries:
        return {
            "average_mood": None,
            "average_energy": None,
            "average_stress": None,
            "entries_count": 0,
            "mood_distribution": {}
        }
    
    # Calculate averages
    mood_scores = [entry.mood_score for entry in mood_entries]
    energy_levels = [entry.energy_level for entry in mood_entries if entry.energy_level]
    stress_levels = [entry.stress_level for entry in mood_entries if entry.stress_level]
    
    # Mood distribution
    mood_distribution = {}
    for score in mood_scores:
        mood_distribution[score] = mood_distribution.get(score, 0) + 1
    
    return {
        "average_mood": round(sum(mood_scores) / len(mood_scores), 2),
        "average_energy": round(sum(energy_levels) / len(energy_levels), 2) if energy_levels else None,
        "average_stress": round(sum(stress_levels) / len(stress_levels), 2) if stress_levels else None,
        "entries_count": len(mood_entries),
        "mood_distribution": mood_distribution,
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }
