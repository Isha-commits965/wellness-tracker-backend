from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, habits, moods, journal, analytics, goals

# Note: Database tables are created via Alembic migrations
# Run 'alembic upgrade head' to apply migrations

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive wellness tracking API with habit tracking, mood monitoring, and AI-powered journaling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wellness-tracker-frontend-5kzj.onrender.com",  # Production frontend
        "http://localhost:5173",  # Local development (Vite)
        "http://localhost:3000",  # Alternative local port
        "http://localhost:8080",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(moods.router, prefix="/moods", tags=["Moods"])
app.include_router(journal.router, prefix="/journal", tags=["Journal"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(goals.router, prefix="/goals", tags=["Goals"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Wellness Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
