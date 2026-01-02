from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import UserResponse, SkillResponse
from app.models.user import User
from app.models.skill import UserSkill

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get the current user's information."""
    return current_user


@router.get("/me/skills", response_model=List[SkillResponse])
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all skill assessments for the current user."""
    skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    return skills


@router.get("/me/skills/{domain}", response_model=List[SkillResponse])
async def get_user_skills_by_domain(
    domain: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill assessments for a specific domain."""
    skills = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.domain == domain
    ).all()
    return skills
