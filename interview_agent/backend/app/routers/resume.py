from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import ResumeParseResponse
from app.models.user import User
from app.models.session import InterviewSession
from app.services.document_intel import parse_resume

router = APIRouter(prefix="/v1/resume", tags=["resume"])


@router.post("/parse", response_model=ResumeParseResponse)
async def upload_and_parse_resume(
    session_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume for the current session."""
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Get the session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "active"
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found"
        )

    # Read file content
    content = await file.read()

    # Parse resume using Azure Document Intelligence
    try:
        resume_text = await parse_resume(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )

    # Update session with resume text
    session.resume_text = resume_text
    db.commit()

    return ResumeParseResponse(
        text=resume_text,
        parsed_at=datetime.utcnow()
    )
