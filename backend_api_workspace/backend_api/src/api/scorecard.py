from fastapi import APIRouter


router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/test")
def scorecard_test():
    """Test endpoint for ScoreCard router to verify registration."""
    return {"message": "ScoreCard router active"}
