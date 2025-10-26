from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import User, Habit, HabitCheckIn, MoodEntry, JournalEntry
from app.schemas import (
    HabitStreak, MoodTrend, WeeklyStats
)
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get habits data
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    # Get today's check-ins
    today_check_ins = db.query(HabitCheckIn).filter(
        HabitCheckIn.user_id == current_user.id,
        HabitCheckIn.date == today
    ).all()
    
    # Get weekly check-ins
    weekly_check_ins = db.query(HabitCheckIn).filter(
        HabitCheckIn.user_id == current_user.id,
        HabitCheckIn.date >= week_start,
        HabitCheckIn.date <= week_end
    ).all()
    
    # Get mood data
    recent_mood = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date == today
    ).first()
    
    # Get journal entries
    recent_journal = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.date == today
    ).first()
    
    # Calculate statistics
    total_habits = len(habits)
    completed_today = len([c for c in today_check_ins if c.completed])
    completion_rate_today = (completed_today / total_habits * 100) if total_habits > 0 else 0
    
    # Weekly completion rate
    weekly_completed = len([c for c in weekly_check_ins if c.completed])
    weekly_total = total_habits * 7  # Assuming daily habits
    weekly_completion_rate = (weekly_completed / weekly_total * 100) if weekly_total > 0 else 0
    
    # Calculate streaks
    habit_streaks = []
    for habit in habits:
        check_ins = db.query(HabitCheckIn).filter(
            HabitCheckIn.habit_id == habit.id,
            HabitCheckIn.completed == True
        ).order_by(HabitCheckIn.date.desc()).all()
        
        current_streak = 0
        if check_ins:
            current_date = today
            for check_in in check_ins:
                if check_in.date == current_date or check_in.date == current_date - timedelta(days=current_streak):
                    current_streak += 1
                    current_date = check_in.date - timedelta(days=1)
                else:
                    break
        
        habit_streaks.append({
            "habit_id": habit.id,
            "habit_name": habit.name,
            "current_streak": current_streak
        })
    
    return {
        "date": today.isoformat(),
        "habits": {
            "total": total_habits,
            "completed_today": completed_today,
            "completion_rate_today": round(completion_rate_today, 1)
        },
        "weekly_stats": {
            "completed": weekly_completed,
            "completion_rate": round(weekly_completion_rate, 1)
        },
        "mood": {
            "today": {
                "score": recent_mood.mood_score if recent_mood else None,
                "energy": recent_mood.energy_level if recent_mood else None,
                "stress": recent_mood.stress_level if recent_mood else None
            }
        },
        "journal": {
            "entry_today": recent_journal is not None,
            "mood_improvement": recent_journal.mood_after - recent_journal.mood_before if recent_journal and recent_journal.mood_before and recent_journal.mood_after else None
        },
        "streaks": habit_streaks
    }


@router.get("/habits/streaks", response_model=List[HabitStreak])
async def get_habit_streaks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed streak information for all habits"""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    streaks = []
    today = date.today()
    
    for habit in habits:
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
        current_date = today
        
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


@router.get("/moods/trends", response_model=List[MoodTrend])
async def get_mood_trends(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mood trends over a specified period"""
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


@router.get("/weekly-stats", response_model=List[WeeklyStats])
async def get_weekly_stats(
    weeks: int = 4,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly statistics for the specified number of weeks"""
    today = date.today()
    stats = []
    
    for week in range(weeks):
        week_start = today - timedelta(days=today.weekday() + (week * 7))
        week_end = week_start + timedelta(days=6)
        
        # Get habits for this week
        habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            Habit.is_active == True
        ).all()
        
        # Get check-ins for this week
        check_ins = db.query(HabitCheckIn).filter(
            HabitCheckIn.user_id == current_user.id,
            HabitCheckIn.date >= week_start,
            HabitCheckIn.date <= week_end
        ).all()
        
        # Get mood entries for this week
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.date >= week_start,
            MoodEntry.date <= week_end
        ).all()
        
        # Get journal entries for this week
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == current_user.id,
            JournalEntry.date >= week_start,
            JournalEntry.date <= week_end
        ).all()
        
        # Calculate statistics
        habits_completed = len([c for c in check_ins if c.completed])
        total_habits = len(habits) * 7  # Assuming daily habits
        
        average_mood = None
        if mood_entries:
            mood_scores = [entry.mood_score for entry in mood_entries]
            average_mood = round(sum(mood_scores) / len(mood_scores), 2)
        
        stats.append(WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            habits_completed=habits_completed,
            total_habits=total_habits,
            average_mood=average_mood,
            journal_entries=len(journal_entries)
        ))
    
    return stats


@router.get("/calendar/{year}/{month}")
async def get_calendar_data(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get calendar data for a specific month"""
    from calendar import monthrange
    
    # Get the first and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Get all check-ins for the month
    check_ins = db.query(HabitCheckIn).filter(
        HabitCheckIn.user_id == current_user.id,
        HabitCheckIn.date >= first_day,
        HabitCheckIn.date <= last_day
    ).all()
    
    # Get mood entries for the month
    mood_entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= first_day,
        MoodEntry.date <= last_day
    ).all()
    
    # Get journal entries for the month
    journal_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.date >= first_day,
        JournalEntry.date <= last_day
    ).all()
    
    # Organize data by date
    calendar_data = {}
    
    # Initialize all days in the month
    current_date = first_day
    while current_date <= last_day:
        calendar_data[current_date.isoformat()] = {
            "habits_completed": 0,
            "total_habits": 0,
            "mood_score": None,
            "journal_entry": False
        }
        current_date += timedelta(days=1)
    
    # Populate with check-ins
    for check_in in check_ins:
        date_str = check_in.date.isoformat()
        if date_str in calendar_data:
            if check_in.completed:
                calendar_data[date_str]["habits_completed"] += 1
            calendar_data[date_str]["total_habits"] += 1
    
    # Populate with mood entries
    for mood_entry in mood_entries:
        date_str = mood_entry.date.isoformat()
        if date_str in calendar_data:
            calendar_data[date_str]["mood_score"] = mood_entry.mood_score
    
    # Populate with journal entries
    for journal_entry in journal_entries:
        date_str = journal_entry.date.isoformat()
        if date_str in calendar_data:
            calendar_data[date_str]["journal_entry"] = True
    
    return {
        "year": year,
        "month": month,
        "data": calendar_data
    }
