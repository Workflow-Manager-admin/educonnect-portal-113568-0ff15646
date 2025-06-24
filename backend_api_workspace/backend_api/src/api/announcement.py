# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from .database import get_db
from .models import Announcement, User
from pydantic import BaseModel, Field
from sqlalchemy.future import select
from sqlalchemy import desc

from .auth import get_current_user, admin_required


router = APIRouter()


# ----------------- SCHEMAS -----------------


class AnnouncementCreate(BaseModel):
    title: str = Field(..., description="Title of announcement")
    message: str = Field(..., description="Message body")
    audience: Optional[str] = Field(
        None,
        description=(
            "Audience for the announcement "
            "(all, students, admin, class:X)"
        )
    )


class AnnouncementOut(BaseModel):
    id: int
    title: str
    message: str
    audience: Optional[str]
    created_at: str

    class Config:
        orm_mode = True


# ----------------- ROUTES -----------------


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=List[AnnouncementOut],
    summary="List all announcements",
    tags=["Announcements"],
)
async def list_announcements(
    search: Optional[str] = None,
    audience: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List announcements, filter by audience or keyword (students see their class/all, admins see all).
    """
    stmt = select(Announcement)
    if audience:
        stmt = stmt.where(Announcement.audience == audience)
    if search:
        stmt = stmt.where(Announcement.title.ilike(f"%{search}%"))
    stmt = stmt.order_by(desc(Announcement.created_at))
    result = await db.execute(stmt)
    return result.scalars().all()


# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=AnnouncementOut,
    summary="Create new announcement (admin)",
)
async def create_announcement(
    ann: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    Admin-only: Create a new announcement.
    """
    new_ann = Announcement(
        title=ann.title,
        message=ann.message,
        audience=ann.audience
    )
    db.add(new_ann)
    await db.commit()
    await db.refresh(new_ann)
    return new_ann


# PUBLIC_INTERFACE
@router.get(
    "/{id}",
    response_model=AnnouncementOut,
    summary="Get single announcement",
)
async def get_announcement(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get details of a single announcement.
    """
    result = await db.execute(
        select(Announcement).where(Announcement.id == id)
    )
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found",
        )
    return ann


# PUBLIC_INTERFACE
@router.put(
    "/{id}",
    response_model=AnnouncementOut,
    summary="Update announcement (admin)",
)
async def update_announcement(
    id: int,
    ann: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    Admin-only: Update an announcement.
    """
    result = await db.execute(select(Announcement).where(Announcement.id == id))
    announcement = result.scalar_one_or_none()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    announcement.title = ann.title
    announcement.message = ann.message
    announcement.audience = ann.audience
    await db.commit()
    await db.refresh(announcement)
    return announcement


# PUBLIC_INTERFACE
@router.delete(
    "/{id}",
    status_code=204,
    summary="Delete announcement (admin)",
)
async def delete_announcement(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    Admin-only: Delete an announcement.
    """
    result = await db.execute(select(Announcement).where(Announcement.id == id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    await db.delete(ann)
    await db.commit()
    return
