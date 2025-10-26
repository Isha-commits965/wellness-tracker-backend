from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import User, Habit, HabitCheckIn
from app.schemas import (
    HabitCreate, HabitUpdate, Habit as HabitSchema,
    HabitCheckInCreate, HabitCheckInUpdate, HabitCheckIn as HabitCheckInSchema,
    HabitStreak
)
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=HabitSchema)
async def create_habit(
    habit: HabitCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new habit"""
    db_habit = Habit(
        user_id=current_user.id,
        name=habit.name,
        description=habit.description,
        category=habit.category,
        target_frequency=habit.target_frequency
    )
    
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    
    return db_habit


@router.get("/", response_model=List[HabitSchema])
async def get_habits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all habits for the current user"""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    return habits


@router.get("/{habit_id}", response_model=HabitSchema)
async def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return habit


@router.put("/{habit_id}", response_model=HabitSchema)
async def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    for field, value in habit_update.dict(exclude_unset=True).items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    
    return habit


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a habit (soft delete)"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    habit.is_active = False
    db.commit()
    
    return {"message": "Habit deleted successfully"}


# Habit Check-ins
@router.post("/check-ins/", response_model=HabitCheckInSchema)
async def create_habit_check_in(
    check_in: HabitCheckInCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a habit check-in"""
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == check_in.habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Check if check-in already exists for this date
    existing_check_in = db.query(HabitCheckIn).filter(
        HabitCheckIn.user_id == current_user.id,
        HabitCheckIn.habit_id == check_in.habit_id,
        HabitCheckIn.date == check_in.date
    ).first()
    
    if existing_check_in:
        # Update existing check-in
        existing_check_in.completed = check_in.completed
        existing_check_in.notes = check_in.notes
        db.commit()
        db.refresh(existing_check_in)
        return existing_check_in
    
    # Create new check-in
    db_check_in = HabitCheckIn(
        user_id=current_user.id,
        habit_id=check_in.habit_id,
        date=check_in.date,
        completed=check_in.completed,
        notes=check_in.notes
    )
    
    db.add(db_check_in)
    db.commit()
    db.refresh(db_check_in)
    
    return db_check_in


@router.get("/check-ins/", response_model=List[HabitCheckInSchema])
async def get_habit_check_ins(
    habit_id: int = None,
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get habit check-ins with optional filters"""
    query = db.query(HabitCheckIn).filter(HabitCheckIn.user_id == current_user.id)
    
    if habit_id:
        query = query.filter(HabitCheckIn.habit_id == habit_id)
    
    if start_date:
        query = query.filter(HabitCheckIn.date >= start_date)
    
    if end_date:
        query = query.filter(HabitCheckIn.date <= end_date)
    
    check_ins = query.order_by(HabitCheckIn.date.desc()).all()
    
    return check_ins


@router.put("/check-ins/{check_in_id}", response_model=HabitCheckInSchema)
async def update_habit_check_in(
    check_in_id: int,
    check_in_update: HabitCheckInUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a habit check-in"""
    check_in = db.query(HabitCheckIn).filter(
        HabitCheckIn.id == check_in_id,
        HabitCheckIn.user_id == current_user.id
    ).first()
    
    if not check_in:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    for field, value in check_in_update.dict(exclude_unset=True).items():
        setattr(check_in, field, value)
    
    db.commit()
    db.refresh(check_in)
    
    return check_in


@router.get("/streaks/", response_model=List[HabitStreak])
async def get_habit_streaks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current streaks for all habits"""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    streaks = []
    
    for habit in habits:
        # Get check-ins ordered by date
        check_ins = db.query(HabitCheckIn).filter(
            HabitCheckIn.habit_id == habit.id,
            HabitCheckIn.completed == True
        ).order_by(HabitCheckIn.date.desc()).all()
        
        if not check_ins:
            streaks.append(HabitStreak(
                habit_id=habit.id,
                habit_name=habit.name,
                current_streak=0,
                longest_streak=0,
                last_completed=None
            ))
            continue
        
        # Calculate current streak
        current_streak = 0
        current_date = date.today()
        
        for check_in in check_ins:
            if check_in.date == current_date or check_in.date == current_date - timedelta(days=current_streak):
                current_streak += 1
                current_date = check_in.date - timedelta(days=1)
            else:
                break
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        prev_date = None
        
        for check_in in check_ins:
            if prev_date is None or check_in.date == prev_date - timedelta(days=1):
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
            prev_date = check_in.date
        
        longest_streak = max(longest_streak, temp_streak)
        
        streaks.append(HabitStreak(
            habit_id=habit.id,
            habit_name=habit.name,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_completed=check_ins[0].date if check_ins else None
        ))
    
    return streaks
