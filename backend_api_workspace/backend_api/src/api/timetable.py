from fastapi import APIRouter


router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/test")
def timetable_test():
    """Test endpoint for Timetable router to verify registration."""
    return {"message": "Timetable router active"}
