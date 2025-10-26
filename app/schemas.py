from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


# Habit Schemas
class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_frequency: str = "daily"


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_frequency: Optional[str] = None
    is_active: Optional[bool] = None


class Habit(HabitBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


# Habit Check-in Schemas
class HabitCheckInBase(BaseModel):
    habit_id: int
    date: date
    completed: bool = False
    notes: Optional[str] = None


class HabitCheckInCreate(HabitCheckInBase):
    pass


class HabitCheckInUpdate(BaseModel):
    completed: Optional[bool] = None
    notes: Optional[str] = None


class HabitCheckIn(HabitCheckInBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


# Mood Entry Schemas
class MoodEntryBase(BaseModel):
    date: date
    mood_score: int
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None
    notes: Optional[str] = None


class MoodEntryCreate(MoodEntryBase):
    pass


class MoodEntryUpdate(BaseModel):
    mood_score: Optional[int] = None
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None
    notes: Optional[str] = None


class MoodEntry(MoodEntryBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    content: str
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None


class JournalEntryCreate(JournalEntryBase):
    date: Optional[date] = None


class JournalEntryUpdate(BaseModel):
    content: Optional[str] = None
    mood_before: Optional[int] = None


class JournalEntry(JournalEntryBase):
    id: int
    user_id: int
    ai_response: Optional[str] = None
    mood_after: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True


# Goal Schemas
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[date] = None
    is_completed: Optional[bool] = None


class Goal(GoalBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


# Analytics Schemas
class HabitStreak(BaseModel):
    habit_id: int
    habit_name: str
    current_streak: int
    longest_streak: int
    last_completed: Optional[date] = None


class MoodTrend(BaseModel):
    date: date
    mood_score: float
    energy_level: Optional[float] = None
    stress_level: Optional[float] = None


class WeeklyStats(BaseModel):
    week_start: date
    week_end: date
    habits_completed: int
    total_habits: int
    average_mood: Optional[float] = None
    journal_entries: int


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# AI Response Schema
class AIJournalResponse(BaseModel):
    response: str
    mood_after: Optional[int] = None
    suggestions: Optional[List[str]] = None
