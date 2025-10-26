from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models import User, Goal
from app.schemas import (
    GoalCreate, GoalUpdate, Goal as GoalSchema
)
from app.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=GoalSchema)
async def create_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new goal"""
    db_goal = Goal(
        user_id=current_user.id,
        title=goal.title,
        description=goal.description,
        target_date=goal.target_date
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return db_goal


@router.get("/", response_model=List[GoalSchema])
async def get_goals(
    completed: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all goals for the current user with optional completion filter"""
    query = db.query(Goal).filter(Goal.user_id == current_user.id)
    
    if completed is not None:
        query = query.filter(Goal.is_completed == completed)
    
    goals = query.order_by(Goal.created_at.desc()).all()
    
    return goals


@router.get("/{goal_id}", response_model=GoalSchema)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal"""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return goal


@router.put("/{goal_id}", response_model=GoalSchema)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a goal"""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for field, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    
    return goal


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a goal"""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Goal deleted successfully"}


@router.post("/{goal_id}/complete")
async def complete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a goal as completed"""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal.is_completed = True
    db.commit()
    
    return {"message": "Goal marked as completed"}


@router.get("/stats/overview")
async def get_goals_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get goals overview statistics"""
    total_goals = db.query(Goal).filter(Goal.user_id == current_user.id).count()
    completed_goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.is_completed == True
    ).count()
    
    # Goals due soon (within 7 days)
    from datetime import timedelta
    soon_due_date = date.today() + timedelta(days=7)
    due_soon = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.is_completed == False,
        Goal.target_date <= soon_due_date,
        Goal.target_date >= date.today()
    ).count()
    
    # Overdue goals
    overdue = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.is_completed == False,
        Goal.target_date < date.today()
    ).count()
    
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    return {
        "total_goals": total_goals,
        "completed_goals": completed_goals,
        "completion_rate": round(completion_rate, 1),
        "due_soon": due_soon,
        "overdue": overdue
    }
