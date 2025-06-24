from fastapi import APIRouter


router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/test")
def auth_test():
    """Test endpoint for Auth router to verify registration."""
    return {"message": "Auth router active"}
