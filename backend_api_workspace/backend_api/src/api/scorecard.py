from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import desc
import json

from .database import get_db
from .models import ScoreCard, User
from .auth import get_current_user, admin_required

router = APIRouter()


class ScoreCardCreate(BaseModel):
    student_id: int = Field(..., description="Student user ID")
    exam_name: str = Field(..., description="Exam name")
    marks_json: dict = Field(..., description="Dictionary of subject: marks")


class ScoreCardOut(BaseModel):
    id: int
    student_id: int
    exam_name: str
    marks_json: dict
    created_at: str

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=ScoreCardOut,
    summary="Create a new scorecard (admin only)",
    tags=["scorecard"]
)
async def create_scorecard(
    card: ScoreCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    score = ScoreCard(
        student_id=card.student_id,
        exam_name=card.exam_name,
        marks_json=json.dumps(card.marks_json),
    )
    db.add(score)
    await db.commit()
    await db.refresh(score)
    score.marks_json = json.loads(score.marks_json)
    return score


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=List[ScoreCardOut],
    summary="List/view scorecards (students & admin)",
    description=(
        "List all scorecards (admin) or only own card (student); "
        "filter by exam name."
    ),
    tags=["scorecard"]
)
async def list_scorecards(
    exam_name: Optional[str] = Query(None, description="Filter by exam name"),
    student_id: Optional[int] = Query(
        None,
        description="Filter by student ID (admin only)",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(ScoreCard)
    if exam_name:
        stmt = stmt.where(ScoreCard.exam_name == exam_name)
    if current_user.role == "student":
        stmt = stmt.where(ScoreCard.student_id == current_user.id)
    elif student_id:
        stmt = stmt.where(ScoreCard.student_id == student_id)
    stmt = stmt.order_by(desc(ScoreCard.created_at))
    result = await db.execute(stmt)
    cards = result.scalars().all()
    # Deserialize marks_json for all entries
    for card in cards:
        card.marks_json = json.loads(card.marks_json)
    return cards


# PUBLIC_INTERFACE
@router.get(
    "/{id}",
    response_model=ScoreCardOut,
    summary="Get a single scorecard (by id)",
    tags=["scorecard"]
)
async def get_scorecard(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ScoreCard).where(ScoreCard.id == id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    # Student can only access their own scorecard
    if (current_user.role == "student" and card.student_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    card.marks_json = json.loads(card.marks_json)
    return card
