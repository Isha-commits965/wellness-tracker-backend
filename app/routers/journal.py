from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import User, JournalEntry
from app.schemas import (
    JournalEntryCreate, JournalEntryUpdate, JournalEntry as JournalEntrySchema,
    AIJournalResponse
)
from app.auth import get_current_active_user
from app.ai_service import ai_journal_service

router = APIRouter()


@router.post("/", response_model=JournalEntrySchema)
async def create_journal_entry(
    journal_entry: JournalEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new journal entry with AI response"""
    # Check if entry already exists for this date
    existing_entry = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.date == journal_entry.date
    ).first()
    
    if existing_entry:
        raise HTTPException(
            status_code=400,
            detail="Journal entry already exists for this date. Use PUT to update."
        )
    
    # Get recent journal entries for context
    recent_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id
    ).order_by(JournalEntry.date.desc()).limit(3).all()
    
    previous_contents = [entry.content for entry in recent_entries]
    
    # Generate AI response
    ai_response = await ai_journal_service.generate_journal_response(
        journal_content=journal_entry.content,
        mood_before=journal_entry.mood_before,
        previous_entries=previous_contents
    )
    
    # Create journal entry
    db_journal_entry = JournalEntry(
        user_id=current_user.id,
        date=journal_entry.date,
        content=journal_entry.content,
        mood_before=journal_entry.mood_before,
        ai_response=ai_response.response,
        mood_after=ai_response.mood_after
    )
    
    db.add(db_journal_entry)
    db.commit()
    db.refresh(db_journal_entry)
    
    return db_journal_entry


@router.get("/", response_model=List[JournalEntrySchema])
async def get_journal_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get journal entries with optional date filters"""
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id)
    
    if start_date:
        query = query.filter(JournalEntry.date >= start_date)
    
    if end_date:
        query = query.filter(JournalEntry.date <= end_date)
    
    journal_entries = query.order_by(JournalEntry.date.desc()).all()
    
    return journal_entries


@router.get("/{entry_id}", response_model=JournalEntrySchema)
async def get_journal_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific journal entry"""
    journal_entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    return journal_entry


@router.put("/{entry_id}", response_model=JournalEntrySchema)
async def update_journal_entry(
    entry_id: int,
    journal_update: JournalEntryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a journal entry and regenerate AI response"""
    journal_entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    # Update fields
    for field, value in journal_update.dict(exclude_unset=True).items():
        setattr(journal_entry, field, value)
    
    # Regenerate AI response if content was updated
    if journal_update.content is not None:
        # Get recent journal entries for context
        recent_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == current_user.id,
            JournalEntry.id != entry_id
        ).order_by(JournalEntry.date.desc()).limit(3).all()
        
        previous_contents = [entry.content for entry in recent_entries]
        
        # Generate new AI response
        ai_response = await ai_journal_service.generate_journal_response(
            journal_content=journal_entry.content,
            mood_before=journal_entry.mood_before,
            previous_entries=previous_contents
        )
        
        journal_entry.ai_response = ai_response.response
        journal_entry.mood_after = ai_response.mood_after
    
    db.commit()
    db.refresh(journal_entry)
    
    return journal_entry


@router.delete("/{entry_id}")
async def delete_journal_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a journal entry"""
    journal_entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    db.delete(journal_entry)
    db.commit()
    
    return {"message": "Journal entry deleted successfully"}


@router.post("/{entry_id}/regenerate-ai", response_model=AIJournalResponse)
async def regenerate_ai_response(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate AI response for a journal entry"""
    journal_entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    # Get recent journal entries for context
    recent_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.id != entry_id
    ).order_by(JournalEntry.date.desc()).limit(3).all()
    
    previous_contents = [entry.content for entry in recent_entries]
    
    # Generate new AI response
    ai_response = await ai_journal_service.generate_journal_response(
        journal_content=journal_entry.content,
        mood_before=journal_entry.mood_before,
        previous_entries=previous_contents
    )
    
    # Update the journal entry
    journal_entry.ai_response = ai_response.response
    journal_entry.mood_after = ai_response.mood_after
    
    db.commit()
    
    return ai_response


@router.get("/stats/weekly")
async def get_weekly_journal_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly journal statistics"""
    # Get last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    journal_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.date >= start_date,
        JournalEntry.date <= end_date
    ).all()
    
    if not journal_entries:
        return {
            "entries_count": 0,
            "average_mood_before": None,
            "average_mood_after": None,
            "mood_improvement": None,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    # Calculate statistics
    mood_before_scores = [entry.mood_before for entry in journal_entries if entry.mood_before]
    mood_after_scores = [entry.mood_after for entry in journal_entries if entry.mood_after]
    
    average_mood_before = round(sum(mood_before_scores) / len(mood_before_scores), 2) if mood_before_scores else None
    average_mood_after = round(sum(mood_after_scores) / len(mood_after_scores), 2) if mood_after_scores else None
    
    mood_improvement = None
    if average_mood_before and average_mood_after:
        mood_improvement = round(average_mood_after - average_mood_before, 2)
    
    return {
        "entries_count": len(journal_entries),
        "average_mood_before": average_mood_before,
        "average_mood_after": average_mood_after,
        "mood_improvement": mood_improvement,
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }
