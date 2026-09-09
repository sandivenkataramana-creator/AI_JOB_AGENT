from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.adapters.job_sources.registry import job_source_registry

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User

from app.schemas.job_schema import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
)
from app.schemas.job_search_schema import (
    JobSearchRequest,
    JobSearchResponse,
)
from app.services.job_service import job_service
from app.services.job_search_service import job_search_service
from app.services.job_match_service import job_match_service
from app.services.resume_profile_service import resume_profile_service
from app.services.resume_intelligence_service import resume_intelligence_service
from app.services.job_description_analyzer import job_description_analyzer
from app.services.job_matching_service import job_matching_service

from app.schemas.job_match_schema import (
    JobMatchResponse,
    JobMatchListResponse,
    JobMatchAllResponse,
)
from app.repositories.resume_repository import resume_repository


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return job_service.create_job(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "",
    response_model=JobListResponse,
)
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jobs = job_service.get_jobs(
        db=db,
        user_id=current_user.id,
    )

    return JobListResponse(
        jobs=jobs,
        total=len(jobs),
    )


@router.post(
    "/search",
    response_model=JobSearchResponse,
)
def search_jobs(
    data: JobSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    adapters = job_source_registry.get_adapters()

    results = job_search_service.search(
        criteria=data,
        adapters=adapters,
    )

    saved_jobs = job_search_service.save_results(
        db=db,
        user_id=current_user.id,
        results=results,
    )

    return JobSearchResponse(
        jobs=results,
        saved_jobs=len(saved_jobs),
        total=len(results),
    )

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return job_service.get_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )


@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: str,
    data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return job_service.update_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
        data=data,
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job_service.delete_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )


@router.post(
    "/{job_id}/match/{resume_id}",
)
def match_job_with_resume(
    job_id: str,
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = job_service.get_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )

    profile = resume_profile_service.get_profile_by_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )

    resume_intelligence = resume_intelligence_service.analyze_profile(
        profile
    )

    job_analysis = job_description_analyzer.analyze(
        job.description
    )

    match_result = job_matching_service.match(
        resume=resume_intelligence,
        job=job_analysis,
    )

    saved_match = job_match_service.create_or_update_match(
        db=db,
        job_id=job_id,
        resume_id=resume_id,
        match_result=match_result,
    )

    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "match_id": saved_match.id,
        "job": job_analysis,
        "match": match_result,
    }


@router.get(
    "/{job_id}/matches",
    response_model=JobMatchListResponse,
)
def list_job_matches(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job_service.get_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )

    matches = job_match_service.get_job_matches(
        db=db,
        job_id=job_id,
    )

    return JobMatchListResponse(
        matches=matches,
        total=len(matches),
    )


@router.post(
    "/{job_id}/match-all",
    response_model=JobMatchAllResponse,
)
def match_job_with_all_resumes(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = job_service.get_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )

    resumes = resume_repository.get_by_user(
        db=db,
        user_id=current_user.id,
    )

    results = []
    skipped = []

    for resume in resumes:
        try:
            profile = resume_profile_service.get_profile_by_resume(
                db=db,
                user_id=current_user.id,
                resume_id=resume.id,
            )

            resume_intelligence = (
                resume_intelligence_service.analyze_profile(
                    profile
                )
            )

            job_analysis = job_description_analyzer.analyze(
                job.description
            )

            match_result = job_matching_service.match(
                resume=resume_intelligence,
                job=job_analysis,
            )

            saved_match = job_match_service.create_or_update_match(
                db=db,
                job_id=job_id,
                resume_id=resume.id,
                match_result=match_result,
            )

            results.append(
                {
                    "match_id": saved_match.id,
                    "resume_id": resume.id,
                    "filename": resume.original_filename,
                    "match_score": match_result.get(
                        "match_score",
                        0,
                    ),
                    "match_level": match_result.get(
                        "match_level",
                        "Unknown",
                    ),
                    "match": match_result,
                }
            )

        except HTTPException as exc:
            skipped.append(
                {
                    "resume_id": resume.id,
                    "filename": resume.original_filename,
                    "reason": exc.detail,
                }
            )

    return {
        "job_id": job_id,
        "total_resumes": len(resumes),
        "matched_resumes": len(results),
        "skipped_resumes": len(skipped),
        "results": results,
        "skipped": skipped,
    }

@router.get(
    "/{job_id}/match/{resume_id}",
    response_model=JobMatchResponse,
)
def get_job_resume_match(
    job_id: str,
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job_service.get_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
    )

    resume_profile_service.get_profile_by_resume(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )

    return job_match_service.get_match(
        db=db,
        job_id=job_id,
        resume_id=resume_id,
    )