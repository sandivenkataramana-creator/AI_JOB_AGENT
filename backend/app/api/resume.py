from fastapi import APIRouter, Body, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User

from app.schemas.resume_schema import (
    ResumeResponse,
    ResumeTextResponse,
)
from app.schemas.resume_profile_schema import ResumeProfileResponse

from app.services.resume_service import resume_service
from app.services.resume_profile_service import resume_profile_service
from app.services.resume_intelligence_service import resume_intelligence_service
from app.services.job_description_analyzer import job_description_analyzer
from app.services.job_matching_service import job_matching_service

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await resume_service.upload_resume(
        db=db,
        user_id=current_user.id,
        file=file,
    )


@router.get(
    "",
    response_model=list[ResumeResponse],
)
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return resume_service.get_user_resumes(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{resume_id}/download",
)
def download_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return resume_service.download_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )

@router.get(
    "/{resume_id}/text",
    response_model=ResumeTextResponse,
)
def get_resume_text(
    resume_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    resume = resume_service.get_resume_text(
        db=db,
        user_id=user.id,
        resume_id=resume_id,
    )

    return ResumeTextResponse(
        resume_id=resume.id,
        filename=resume.original_filename,
        extracted_text=resume.extracted_text,
    )

@router.get(
    "/{resume_id}/profile",
    response_model=ResumeProfileResponse,
)
def get_resume_profile(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return resume_profile_service.get_profile_by_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )

@router.get(
    "/{resume_id}/intelligence",
)
def get_resume_intelligence(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = resume_profile_service.get_profile_by_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )

    return resume_intelligence_service.analyze_profile(
        profile
    )

@router.post(
    "/{resume_id}/match",
)
def match_resume_with_job(
    resume_id: str,
    job_description: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = resume_profile_service.get_profile_by_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )

    resume_intelligence = resume_intelligence_service.analyze_profile(
        profile
    )

    job_analysis = job_description_analyzer.analyze(
        job_description
    )

    match_result = job_matching_service.match(
        resume=resume_intelligence,
        job=job_analysis,
    )

    return {
        "resume_id": resume_id,
        "job": job_analysis,
        "match": match_result,
    }

@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return resume_service.get_user_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume_service.delete_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )