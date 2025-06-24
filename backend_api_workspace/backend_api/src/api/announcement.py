from fastapi import APIRouter


router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/test")
def announcement_test():
    """Test endpoint for Announcement router to verify registration."""
    return {"message": "Announcement router active"}
