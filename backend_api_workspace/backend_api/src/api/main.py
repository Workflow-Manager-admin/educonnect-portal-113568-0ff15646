from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import auth, timetable, scorecard, announcement

openapi_tags = [
    {
        "name": "auth",
        "description": (
            "Endpoints for user authentication (registration/login), "
            "JWT access token"
        ),
    },
    {
        "name": "timetable",
        "description": (
            "CRUD exam timetable (admin) and timetable lookup/download (student)"
        ),
    },
    {
        "name": "scorecard",
        "description": (
            "CRUD exam score cards (admin) and personal score review (student)"
        ),
    },
    {
        "name": "announcement",
        "description": (
            "Announcements related to exams, paper distribution, PTA meetings, etc."
        ),
    },
]

app = FastAPI(
    title="EduConnect Portal API",
    description=(
        "Backend REST API for EduConnect student portal: authentication, "
        "timetables (PDF upload/download), score cards, announcements, and admin features."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
    contact={
        "name": "EduConnect Team",
        "email": "support@educonnect.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(timetable.router, prefix="/timetable")
app.include_router(scorecard.router, prefix="/scorecard")
app.include_router(announcement.router, prefix="/announcement")


@app.get(
    "/",
    summary="Health check",
    tags=["health"]
)
def health_check():
    """Simple health check for load balancer/monitoring."""
    return {"message": "Healthy"}
