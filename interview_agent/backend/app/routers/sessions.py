from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import SessionCreate, SessionResponse, SessionDetailResponse
from app.models.user import User
from app.models.session import InterviewSession
from app.services.session_manager import session_manager

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new interview session."""
    # Check for active sessions (no concurrent sessions allowed)
    active_session = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "active"
    ).first()

    if active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active session. Please end it first."
        )

    # Validate inputs
    valid_personas = ["friendly", "neutral", "aggressive", "faang", "startup"]
    if session_data.persona not in valid_personas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid persona. Must be one of: {valid_personas}"
        )

    valid_depths = ["surface", "interview_ready", "expert"]
    if session_data.depth_mode not in valid_depths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid depth mode. Must be one of: {valid_depths}"
        )

    valid_domains = ["coding", "system_design", "ml"]
    for domain in session_data.domains:
        if domain not in valid_domains:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid domain '{domain}'. Must be one of: {valid_domains}"
            )

    # Create session in database
    interview_session = InterviewSession(
        user_id=current_user.id,
        persona=session_data.persona,
        depth_mode=session_data.depth_mode,
        domains=session_data.domains,
        declared_weak_areas=session_data.declared_weak_areas
    )
    db.add(interview_session)
    db.commit()
    db.refresh(interview_session)

    # Initialize in-memory session state
    session_manager.create_session(interview_session.id, current_user.id)

    return interview_session


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all sessions for the current user."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.started_at.desc()).all()
    return sessions


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific session."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End an active session (mid-session exit)."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not active"
        )

    # Update session status
    session.status = "terminated"
    session.ended_at = datetime.utcnow()
    db.commit()

    # Clean up in-memory state
    session_manager.end_session(session_id)

    return None
