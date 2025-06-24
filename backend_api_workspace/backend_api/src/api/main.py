from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Attempt to import endpoints for authentication, timetables, score cards, and announcements.
try:
    from . import auth, timetable, scorecard, announcement
except ImportError:
    # If module files don't exist yet, these imports will fail (scaffold warning).
    auth = None
    timetable = None
    scorecard = None
    announcement = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints for each feature module if present
if auth and hasattr(auth, "router"):
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
if timetable and hasattr(timetable, "router"):
    app.include_router(timetable.router, prefix="/timetable", tags=["timetable"])
if scorecard and hasattr(scorecard, "router"):
    app.include_router(scorecard.router, prefix="/scorecard", tags=["scorecard"])
if announcement and hasattr(announcement, "router"):
    app.include_router(announcement.router, prefix="/announcement", tags=["announcement"])


@app.get("/")
def health_check():
    return {"message": "Healthy"}
