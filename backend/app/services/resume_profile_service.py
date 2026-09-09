from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume_profile import ResumeProfile
from app.repositories.resume_profile_repository import (
    resume_profile_repository,
)
from app.repositories.resume_repository import resume_repository
from app.services.skill_extractor import extract_skills_from_text


class ResumeProfileService:

    def get_profile_by_resume(
        self,
        db: Session,
        user_id: str,
        resume_id: str,
    ) -> ResumeProfile:

        resume = resume_repository.get_by_id_and_user(
            db,
            resume_id,
            user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        profile = resume_profile_repository.get_by_resume_id(
            db,
            resume_id,
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume profile not found",
            )

        return profile

    def create_profile(
        self,
        db: Session,
        resume_id: str,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        location: str | None = None,
        summary: str | None = None,
        skills: str | None = None,
        experience: str | None = None,
        education: str | None = None,
        projects: str | None = None,
        certifications: str | None = None,
        resume_text: str | None = None,
    ) -> ResumeProfile:

        existing_profile = (
            resume_profile_repository.get_by_resume_id(
                db,
                resume_id,
            )
        )

        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume profile already exists",
            )

        # Automatically extract skills from the complete resume text
        if resume_text:
            extracted_skills = extract_skills_from_text(
                resume_text
            )

            skills = ", ".join(extracted_skills)

        profile = ResumeProfile(
            resume_id=resume_id,
            full_name=full_name,
            email=email,
            phone=phone,
            location=location,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
        )

        return resume_profile_repository.create(
            db,
            profile,
        )


resume_profile_service = ResumeProfileService()