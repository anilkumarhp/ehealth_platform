from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import os
from pathlib import Path

from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.core.security import TokenPayload
from app.models.file_attachment import FileAttachment
from app.core.config import settings

router = APIRouter()

# File upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_file(
    *,
    db: AsyncSession = Depends(get_db_session),
    file: UploadFile = File(...),
    file_category: str = Form(...),
    test_order_id: Optional[UUID] = Form(None),
    appointment_id: Optional[UUID] = Form(None),
    description: Optional[str] = Form(None),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Upload a file attachment."""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    # Generate unique filename
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create database record
    file_attachment = FileAttachment(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        content_type=file.content_type,
        file_category=file_category,
        test_order_id=test_order_id,
        appointment_id=appointment_id,
        uploaded_by=current_user.sub,
        description=description
    )
    
    db.add(file_attachment)
    await db.flush()
    await db.commit()
    
    return {
        "id": str(file_attachment.id),
        "filename": file_attachment.original_filename,
        "file_category": file_attachment.file_category,
        "file_size": file_attachment.file_size
    }

@router.get("/download/{file_id}")
async def download_file(
    *,
    db: AsyncSession = Depends(get_db_session),
    file_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Download a file attachment."""
    
    # Get file record
    result = await db.execute(
        select(FileAttachment).where(FileAttachment.id == file_id)
    )
    file_attachment = result.scalar_one_or_none()
    
    if not file_attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists
    if not os.path.exists(file_attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        path=file_attachment.file_path,
        filename=file_attachment.original_filename,
        media_type=file_attachment.content_type
    )

@router.get("/list")
async def list_files(
    *,
    db: AsyncSession = Depends(get_db_session),
    test_order_id: Optional[UUID] = None,
    appointment_id: Optional[UUID] = None,
    file_category: Optional[str] = None,
    current_user: TokenPayload = Depends(get_current_user)
):
    """List file attachments with filters."""
    
    from sqlalchemy import select
    query = select(FileAttachment)
    
    if test_order_id:
        query = query.where(FileAttachment.test_order_id == test_order_id)
    if appointment_id:
        query = query.where(FileAttachment.appointment_id == appointment_id)
    if file_category:
        query = query.where(FileAttachment.file_category == file_category)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    return [
        {
            "id": str(f.id),
            "filename": f.original_filename,
            "file_category": f.file_category,
            "file_size": f.file_size,
            "upload_datetime": f.upload_datetime.isoformat(),
            "description": f.description
        }
        for f in files
    ]