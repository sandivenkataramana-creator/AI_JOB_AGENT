import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.job_match import JobMatch
from app.repositories.job_match_repository import job_match_repository


class JobMatchService:

    def create_or_update_match(
        self,
        db: Session,
        job_id: str,
        resume_id: str,
        match_result: dict,
    ) -> JobMatch:

        existing_match = job_match_repository.get_by_job_and_resume(
            db,
            job_id,
            resume_id,
        )

        score_breakdown = match_result.get(
            "score_breakdown",
            {},
        )

        required_skills = match_result.get(
            "required_skills",
            {},
        )

        preferred_skills = match_result.get(
            "preferred_skills",
            {},
        )

        responsibilities = match_result.get(
            "responsibilities",
            {},
        )

        if existing_match:
            job_match = existing_match
        else:
            job_match = JobMatch(
                job_id=job_id,
                resume_id=resume_id,
            )

        job_match.match_score = float(
            match_result.get("match_score", 0)
        )

        job_match.match_level = match_result.get(
            "match_level",
            "Unknown",
        )

        job_match.required_skills_score = self._get_score(
            score_breakdown,
            "required_skills",
        )

        job_match.preferred_skills_score = self._get_score(
            score_breakdown,
            "preferred_skills",
        )

        job_match.experience_score = self._get_score(
            score_breakdown,
            "experience",
        )

        job_match.responsibilities_score = self._get_score(
            score_breakdown,
            "responsibilities",
        )

        job_match.matched_skills = self._serialize(
            required_skills.get("matched", [])
            + preferred_skills.get("matched", [])
        )

        job_match.missing_skills = self._serialize(
            required_skills.get("missing", [])
            + preferred_skills.get("missing", [])
        )

        job_match.strengths = self._serialize(
            match_result.get("strengths", [])
        )

        job_match.skill_gaps = self._serialize(
            match_result.get("skill_gaps", [])
        )

        job_match.recommendations = self._serialize(
            match_result.get("recommendations", [])
        )

        if existing_match:
            db.commit()
            db.refresh(job_match)
            return job_match

        return job_match_repository.create(
            db,
            job_match,
        )

    def get_match(
        self,
        db: Session,
        job_id: str,
        resume_id: str,
    ) -> dict:

        job_match = job_match_repository.get_by_job_and_resume(
            db,
            job_id,
            resume_id,
        )

        if not job_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job match not found",
            )

        return self.to_response_data(job_match)

    def get_job_matches(
        self,
        db: Session,
        job_id: str,
    ) -> list[dict]:

        matches = job_match_repository.get_all_by_job(
            db,
            job_id,
        )

        return [
            self.to_response_data(match)
            for match in matches
        ]

    def get_resume_matches(
        self,
        db: Session,
        resume_id: str,
    ) -> list[dict]:

        matches = job_match_repository.get_all_by_resume(
            db,
            resume_id,
        )

        return [
            self.to_response_data(match)
            for match in matches
        ]

    @staticmethod
    def _get_score(
        score_breakdown: dict,
        key: str,
    ) -> float | None:

        section = score_breakdown.get(key)

        if not section:
            return None

        score = section.get("score")

        if score is None:
            return None

        return float(score)

    @staticmethod
    def _serialize(value: list) -> str:

        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def to_response_data(
        job_match: JobMatch,
    ) -> dict:

        return {
            "id": job_match.id,
            "job_id": job_match.job_id,
            "resume_id": job_match.resume_id,
            "match_score": job_match.match_score,
            "match_level": job_match.match_level,
            "required_skills_score": job_match.required_skills_score,
            "preferred_skills_score": job_match.preferred_skills_score,
            "experience_score": job_match.experience_score,
            "responsibilities_score": job_match.responsibilities_score,
            "matched_skills": JobMatchService._deserialize(
                job_match.matched_skills
            ),
            "missing_skills": JobMatchService._deserialize(
                job_match.missing_skills
            ),
            "strengths": JobMatchService._deserialize(
                job_match.strengths
            ),
            "skill_gaps": JobMatchService._deserialize(
                job_match.skill_gaps
            ),
            "recommendations": JobMatchService._deserialize(
                job_match.recommendations
            ),
            "created_at": job_match.created_at,
            "updated_at": job_match.updated_at,
        }

    @staticmethod
    def _deserialize(value: str | None) -> list[str]:

        if not value:
            return []

        try:
            result = json.loads(value)

            if isinstance(result, list):
                return [
                    str(item)
                    for item in result
                ]

        except (json.JSONDecodeError, TypeError):
            pass

        return []

job_match_service = JobMatchService()
