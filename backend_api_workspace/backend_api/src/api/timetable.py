from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Query,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import desc
import os
import shutil

from .database import get_db
from .models import Timetable, User
from .auth import get_current_user, admin_required

MEDIA_ROOT = "/app/media"
os.makedirs(MEDIA_ROOT, exist_ok=True)

router = APIRouter()


class TimetableOut(BaseModel):
    id: int
    class_name: str
    exam_name: str
    pdf_filename: str
    uploaded_at: str
    uploaded_by: Optional[int]

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
@router.post(
    "/upload",
    response_model=TimetableOut,
    summary="Upload timetable PDF (admin-only)",
    description=(
        "Admins upload a new exam timetable for a class/year, specifying "
        "exam name, class name, and uploading a PDF file."
    ),
    tags=["timetable"],
)
async def upload_timetable(
    class_name: str = Query(..., description="Class for which the timetable is valid"),
    exam_name: str = Query(..., description="Exam name"),
    file_obj: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    # Save uploaded file
    pdf_path = os.path.join(MEDIA_ROOT, file_obj.filename)
    with open(pdf_path, "wb") as dest:
        shutil.copyfileobj(file_obj.file, dest)
    timetable = Timetable(
        class_name=class_name,
        exam_name=exam_name,
        pdf_filename=file_obj.filename,
        uploaded_by=current_user.id if current_user else None,
    )
    db.add(timetable)
    await db.commit()
    await db.refresh(timetable)
    return timetable


# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=List[TimetableOut],
    summary="List/search timetables",
    description=(
        "Get a list of all available exam timetables, optionally filterable "
        "by class or exam name."
    ),
    tags=["timetable"]
)
async def list_timetables(
    class_name: Optional[str] = Query(None, description="Class to filter"),
    exam_name: Optional[str] = Query(None, description="Exam to filter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Timetable)
    if class_name:
        stmt = stmt.where(Timetable.class_name == class_name)
    if exam_name:
        stmt = stmt.where(Timetable.exam_name == exam_name)
    stmt = stmt.order_by(desc(Timetable.uploaded_at))
    result = await db.execute(stmt)
    return result.scalars().all()


# PUBLIC_INTERFACE
@router.get(
    "/download/{id}",
    summary="Download timetable PDF by ID",
    description="Download the PDF for a given timetable ID. Permission required.",
    tags=["timetable"]
)
async def download_timetable(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Timetable).where(Timetable.id == id))
    timetable = result.scalar_one_or_none()
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    pdf_path = os.path.join(MEDIA_ROOT, timetable.pdf_filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404,
            detail="Timetable PDF missing on server"
        )
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
    headers = {
        "Content-Disposition": f'attachment; filename="{timetable.pdf_filename}"'
    }
    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers=headers,
    )


# PUBLIC_INTERFACE
@router.delete(
    "/{id}",
    status_code=204,
    summary="Delete timetable (admin-only)",
    description="Remove a timetable and its associated PDF file (admin only)",
    tags=["timetable"]
)
async def delete_timetable(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    result = await db.execute(select(Timetable).where(Timetable.id == id))
    timetable = result.scalar_one_or_none()
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    # Remove PDF file if possible
    pdf_path = os.path.join(MEDIA_ROOT, timetable.pdf_filename)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    await db.delete(timetable)
    await db.commit()
    return
