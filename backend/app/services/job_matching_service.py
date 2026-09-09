import re
from typing import Any


class JobMatchingService:

    REQUIRED_SKILL_WEIGHT = 50
    PREFERRED_SKILL_WEIGHT = 15
    EXPERIENCE_WEIGHT = 20
    EDUCATION_WEIGHT = 10
    RESPONSIBILITY_WEIGHT = 5

    def match(
        self,
        resume: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:

        resume_skills = self._normalize_skills(
            resume.get("skills", [])
        )

        required_skills = self._normalize_skills(
            job.get("required_skills", [])
        )

        preferred_skills = self._normalize_skills(
            job.get("preferred_skills", [])
        )

        required_matched = [
            skill
            for skill in required_skills
            if self._skill_matches(skill, resume_skills)
        ]

        required_missing = [
            skill
            for skill in required_skills
            if not self._skill_matches(skill, resume_skills)
        ]

        preferred_matched = [
            skill
            for skill in preferred_skills
            if self._skill_matches(skill, resume_skills)
        ]

        preferred_missing = [
            skill
            for skill in preferred_skills
            if not self._skill_matches(skill, resume_skills)
        ]

        required_score = self._percentage(
            len(required_matched),
            len(required_skills),
        )

        preferred_score = self._percentage(
            len(preferred_matched),
            len(preferred_skills),
        )

        experience_result = self._match_experience(
            resume,
            job,
        )

        education_result = self._match_education(
            resume,
            job,
        )

        responsibilities = job.get("responsibilities", [])

        responsibility_result = self._match_responsibilities(
            resume,
            job,
        )

        score_components = []
        total_weight = 0

        if required_skills:
            score_components.append(
                (
                    required_score,
                    self.REQUIRED_SKILL_WEIGHT,
                )
            )
            total_weight += self.REQUIRED_SKILL_WEIGHT

        if preferred_skills:
            score_components.append(
                (
                    preferred_score,
                    self.PREFERRED_SKILL_WEIGHT,
                )
            )
            total_weight += self.PREFERRED_SKILL_WEIGHT

        if job.get("experience"):
            if (
                job["experience"].get("min_years") is not None
                or job["experience"].get("max_years") is not None
            ):
                score_components.append(
                    (
                        experience_result["score"],
                        self.EXPERIENCE_WEIGHT,
                    )
                )
                total_weight += self.EXPERIENCE_WEIGHT

        if job.get("education"):
            score_components.append(
                (
                    education_result["score"],
                    self.EDUCATION_WEIGHT,
                )
            )
            total_weight += self.EDUCATION_WEIGHT

        if responsibilities:
            score_components.append(
                (
                    responsibility_result["score"],
                    self.RESPONSIBILITY_WEIGHT,
                )
            )
            total_weight += self.RESPONSIBILITY_WEIGHT

        if total_weight == 0:
            score = 0
        else:
            score = sum(
                score * weight
                for score, weight in score_components
            ) / total_weight

        score = round(score, 2)
        score_breakdown = {}

        if required_skills:
            score_breakdown["required_skills"] = {
                "weight": self.REQUIRED_SKILL_WEIGHT,
                "score": round(required_score, 2),
                "weighted_score": round(
                    required_score * self.REQUIRED_SKILL_WEIGHT / 100,
                    2,
                ),
            }

        if preferred_skills:
            score_breakdown["preferred_skills"] = {
                "weight": self.PREFERRED_SKILL_WEIGHT,
                "score": round(preferred_score, 2),
                "weighted_score": round(
                    preferred_score * self.PREFERRED_SKILL_WEIGHT / 100,
                    2,
                ),
            }

        if (
            job.get("experience")
            and (
                job["experience"].get("min_years") is not None
                or job["experience"].get("max_years") is not None
            )
        ):
            score_breakdown["experience"] = {
                "weight": self.EXPERIENCE_WEIGHT,
                "score": round(
                    experience_result["score"],
                    2,
                ),
                "weighted_score": round(
                    experience_result["score"]
                    * self.EXPERIENCE_WEIGHT
                    / 100,
                    2,
                ),
            }

        if job.get("education"):
            score_breakdown["education"] = {
                "weight": self.EDUCATION_WEIGHT,
                "score": round(
                    education_result["score"],
                    2,
                ),
                "weighted_score": round(
                    education_result["score"]
                    * self.EDUCATION_WEIGHT
                    / 100,
                    2,
                ),
            }

        if responsibilities:
            score_breakdown["responsibilities"] = {
                "weight": self.RESPONSIBILITY_WEIGHT,
                "score": round(
                    responsibility_result["score"],
                    2,
                ),
                "weighted_score": round(
                    responsibility_result["score"]
                    * self.RESPONSIBILITY_WEIGHT
                    / 100,
                    2,
                ),
            }

        strengths = list(required_matched)

        for skill in preferred_matched:
            if skill not in strengths:
                strengths.append(skill)

        skill_gaps = list(required_missing)

        for skill in preferred_missing:
            if skill not in skill_gaps:
                skill_gaps.append(skill)

        return {
            "match_score": score,
            "match_level": self._match_level(score),
            "score_breakdown": score_breakdown,

            "required_skills": {
                "matched": required_matched,
                "missing": required_missing,
                "score": round(required_score, 2),
            },

            "preferred_skills": {
                "matched": preferred_matched,
                "missing": preferred_missing,
                "score": round(preferred_score, 2),
            },

            "experience": experience_result,

            "education": education_result,

            "responsibilities": responsibility_result,

            "strengths": strengths,

            "skill_gaps": skill_gaps,

            "recommendations": self._recommendations(
                required_missing,
                preferred_missing,
                experience_result,
            ),
        }

    # =========================================================
    # SKILLS
    # =========================================================

    @staticmethod
    def _normalize_skills(
        skills: Any,
    ) -> list[str]:

        if not skills:
            return []

        if isinstance(skills, str):
            skills = [
                item.strip()
                for item in skills.split(",")
                if item.strip()
            ]

        result = []
        seen = set()

        for skill in skills:

            if not skill:
                continue

            normalized = re.sub(
                r"\s+",
                " ",
                str(skill).strip().lower(),
            )

            key = normalized

            if key in seen:
                continue

            seen.add(key)
            result.append(str(skill).strip())

        return result

    @staticmethod
    def _skill_matches(
        required_skill: str,
        resume_skills: list[str],
    ) -> bool:

        required = re.sub(
            r"\s+",
            " ",
            required_skill.lower().strip(),
        )

        aliases = {
            "react": ["react", "react.js", "reactjs"],
            "react.js": ["react", "react.js", "reactjs"],
            "reactjs": ["react", "react.js", "reactjs"],

            "node": ["node", "node.js", "nodejs"],
            "node.js": ["node", "node.js", "nodejs"],
            "nodejs": ["node", "node.js", "nodejs"],

            "express": [
                "express",
                "express.js",
                "expressjs",
            ],
            "express.js": [
                "express",
                "express.js",
                "expressjs",
            ],
            "expressjs": [
                "express",
                "express.js",
                "expressjs",
            ],

            "postgres": [
                "postgres",
                "postgresql",
            ],
            "postgresql": [
                "postgres",
                "postgresql",
            ],

            "rest api": [
                "rest api",
                "rest apis",
                "restful api",
                "restful apis",
                "restapi",
                "restapis",
            ],

            "rest apis": [
                "rest api",
                "rest apis",
                "restful api",
                "restful apis",
                "restapi",
                "restapis",
            ],

            "restful api": [
                "rest api",
                "rest apis",
                "restful api",
                "restful apis",
                "restapi",
                "restapis",
            ],

            "restful apis": [
                "rest api",
                "rest apis",
                "restful api",
                "restful apis",
                "restapi",
                "restapis",
            ],

            "restapi": [
                "rest api",
                "rest apis",
                "restful api",
                "restful apis",
                "restapi",
                "restapis",
            ],

            "restapis": [
                "rest api",
                "rest apis",
                "restful api",
                "restful apis",
                "restapi",
                "restapis",
            ],

            "aws": [
                "aws",
                "amazon web services",
            ],

            "amazon web services": [
                "aws",
                "amazon web services",
            ],

            "azure": [
                "azure",
                "microsoft azure",
            ],

            "microsoft azure": [
                "azure",
                "microsoft azure",
            ],

            "gcp": [
                "gcp",
                "google cloud",
            ],

            "google cloud": [
                "gcp",
                "google cloud",
            ],
        }

        accepted = aliases.get(
            required,
            [required],
        )

        normalized_resume_skills = [
            re.sub(
                r"\s+",
                " ",
                str(skill).lower().strip(),
            )
            for skill in resume_skills
        ]

        return any(
            resume_skill in accepted
            for resume_skill in normalized_resume_skills
        )
    # =========================================================
    # EXPERIENCE
    # =========================================================

    def _match_experience(
        self,
        resume: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:

        job_experience = job.get(
            "experience",
            {},
        ) or {}

        required_years = job_experience.get(
            "min_years"
        )

        if required_years is None:
            return {
                "required_years": None,
                "candidate_years": None,
                "matched": True,
                "score": 100,
            }

        candidate_years = self._estimate_experience(
            resume
        )

        matched = candidate_years >= required_years

        if required_years == 0:
            score = 100
        else:
            score = min(
                100,
                (candidate_years / required_years) * 100,
            )

        return {
            "required_years": required_years,
            "candidate_years": round(
                candidate_years,
                2,
            ),
            "matched": matched,
            "score": round(score, 2),
        }

    @staticmethod
    def _estimate_experience(
        resume: dict[str, Any],
    ) -> float:

        experience = resume.get(
            "experience"
        )

        if not experience:
            return 0

        entries = []

        if isinstance(experience, dict):
            entries = experience.get(
                "entries",
                []
            )

        if not entries:
            return 0

        total_months = 0

        for entry in entries:

            start = str(
                entry.get(
                    "start_date",
                    ""
                )
            )

            end = str(
                entry.get(
                    "end_date",
                    ""
                )
            )

            start_match = re.search(
                r"(19|20)\d{2}",
                start,
            )

            if not start_match:
                continue

            start_year = int(
                start_match.group(0)
            )

            end_match = re.search(
                r"(19|20)\d{2}",
                end,
            )

            if end.lower().strip() == "present":
                from datetime import datetime

                end_year = datetime.now().year
                end_month = datetime.now().month
            elif end_match:
                end_year = int(
                    end_match.group(0)
                )
                end_month = 12
            else:
                continue

            start_month_match = re.search(
                r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
                start.lower(),
            )

            if start_month_match:
                months = {
                    "jan": 1,
                    "feb": 2,
                    "mar": 3,
                    "apr": 4,
                    "may": 5,
                    "jun": 6,
                    "jul": 7,
                    "aug": 8,
                    "sep": 9,
                    "oct": 10,
                    "nov": 11,
                    "dec": 12,
                }

                start_month = months[
                    start_month_match.group(0)
                ]
            else:
                start_month = 1

            months_worked = (
                (end_year - start_year) * 12
                + end_month
                - start_month
                + 1
            )

            if months_worked > 0:
                total_months += months_worked

        return total_months / 12

    # =========================================================
    # EDUCATION
    # =========================================================

    def _match_education(
        self,
        resume: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:

        required = job.get(
            "education",
            []
        ) or []

        if not required:
            return {
                "required": [],
                "matched": True,
                "score": 100,
            }

        resume_education = resume.get(
            "education",
            {}
        ) or {}

        raw_text = str(
            resume_education.get(
                "raw_text",
                ""
            )
        ).lower()

        matched = []

        for requirement in required:

            requirement_text = str(
                requirement
            ).lower()

            if requirement_text in raw_text:
                matched.append(
                    requirement
                )

        score = self._percentage(
            len(matched),
            len(required),
        )

        return {
            "required": required,
            "matched": matched,
            "missing": [
                item
                for item in required
                if item not in matched
            ],
            "score": round(score, 2),
        }

    # =========================================================
    # RESPONSIBILITIES
    # =========================================================

    def _match_responsibilities(
        self,
        resume: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:

        responsibilities = job.get(
            "responsibilities",
            []
        ) or []

        if not responsibilities:
            return {
                "matched": [],
                "score": 100,
            }

        resume_text = self._resume_text(
            resume
        )

        matched = []

        for responsibility in responsibilities:

            keywords = self._keywords(
                responsibility
            )

            if not keywords:
                continue

            matches = sum(
                1
                for keyword in keywords
                if keyword in resume_text
            )

            if matches >= max(
                1,
                len(keywords) // 3,
            ):
                matched.append(
                    responsibility
                )

        score = self._percentage(
            len(matched),
            len(responsibilities),
        )

        return {
            "matched": matched,
            "missing": [
                item
                for item in responsibilities
                if item not in matched
            ],
            "score": round(score, 2),
        }

    @staticmethod
    def _resume_text(
        resume: dict[str, Any],
    ) -> str:

        parts = [
            resume.get("summary", ""),
        ]

        experience = resume.get(
            "experience",
            {}
        )

        if isinstance(experience, dict):
            parts.append(
                experience.get("raw_text", "")
            )
        else:
            parts.append(
                str(experience)
            )

        projects = resume.get(
            "projects",
            {}
        )

        if isinstance(projects, dict):
            parts.append(
                projects.get("raw_text", "")
            )
        else:
            parts.append(
                str(projects)
            )

        return " ".join(
            str(part).lower()
            for part in parts
            if part
        )

    @staticmethod
    def _keywords(
        text: str,
    ) -> list[str]:

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z+#.-]{2,}\b",
            text.lower(),
        )

        ignored = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "build",
            "design",
            "develop",
            "using",
            "backend",
            "services",
        }

        return [
            word
            for word in words
            if word not in ignored
        ]

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _percentage(
        matched: int,
        total: int,
    ) -> float:

        if total == 0:
            return 100

        return (
            matched / total
        ) * 100

    @staticmethod
    def _match_level(
        score: float,
    ) -> str:

        if score >= 85:
            return "Excellent Match"

        if score >= 70:
            return "Strong Match"

        if score >= 50:
            return "Moderate Match"

        if score >= 30:
            return "Weak Match"

        return "Poor Match"

    @staticmethod
    def _recommendations(
        required_missing: list[str],
        preferred_missing: list[str],
        experience: dict[str, Any],
    ) -> list[str]:

        recommendations = []

        if required_missing:
            recommendations.append(
                "Improve or gain experience with: "
                + ", ".join(required_missing)
            )

        if preferred_missing:
            recommendations.append(
                "Consider learning preferred skills: "
                + ", ".join(preferred_missing)
            )

        if not experience.get("matched", True):
            recommendations.append(
                "The candidate's experience is below "
                "the minimum requirement."
            )

        if not recommendations:
            recommendations.append(
                "Resume is well aligned with this job."
            )

        return recommendations


job_matching_service = JobMatchingService()