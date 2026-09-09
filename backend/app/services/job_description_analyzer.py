import re

from app.services.skill_extractor import extract_skills_from_text


class JobDescriptionAnalyzer:

    def analyze(self, text: str) -> dict:

        if not text or not text.strip():
            return {
                "raw_text": "",
                "job_title": None,
                "required_skills": [],
                "preferred_skills": [],
                "experience": {
                    "min_years": None,
                    "max_years": None,
                },
                "education": [],
                "responsibilities": [],
            }

        text = self._normalize_text(text)

        return {
            "raw_text": text,
            "job_title": self._extract_job_title(text),
            "required_skills": self._extract_required_skills(text),
            "preferred_skills": self._extract_preferred_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "responsibilities": self._extract_responsibilities(text),
        }

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_text(text: str) -> str:

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        return "\n".join(
            line.strip()
            for line in text.splitlines()
            if line.strip()
        )

    # =========================================================
    # JOB TITLE
    # =========================================================

    def _extract_job_title(self, text: str) -> str | None:

        lines = text.splitlines()

        title_patterns = (
            r"^job\s*title\s*[:\-]\s*(.+)$",
            r"^position\s*[:\-]\s*(.+)$",
            r"^role\s*[:\-]\s*(.+)$",
            r"^designation\s*[:\-]\s*(.+)$",
        )

        for line in lines:

            for pattern in title_patterns:

                match = re.match(
                    pattern,
                    line,
                    re.IGNORECASE,
                )

                if match:
                    return match.group(1).strip()

        # Fallback:
        # use the first short meaningful line.

        for line in lines[:10]:

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in (
                    "job description",
                    "responsibilities",
                    "requirements",
                    "qualifications",
                    "skills",
                )
            ):
                continue

            if 1 <= len(line.split()) <= 8:
                return line.strip()

        return None

    # =========================================================
    # REQUIRED SKILLS
    # =========================================================

    def _extract_required_skills(
        self,
        text: str,
    ) -> list[str]:

        section = self._extract_section(
            text,
            (
                "required skills",
                "requirements",
                "required qualifications",
                "must have",
                "mandatory skills",
                "technical requirements",
            ),
        )

        if not section:
            return []

        return self._extract_skills(section)

    # =========================================================
    # PREFERRED SKILLS
    # =========================================================

    def _extract_preferred_skills(
        self,
        text: str,
    ) -> list[str]:

        section = self._extract_section(
            text,
            (
                "preferred skills",
                "preferred qualifications",
                "nice to have",
                "good to have",
                "desired skills",
                "preferred",
            ),
        )

        if not section:
            return []

        return self._extract_skills(section)

    # =========================================================
    # SKILLS
    # =========================================================

    @staticmethod
    def _extract_skills(
        text: str,
    ) -> list[str]:

        skills = extract_skills_from_text(text)

        result = []

        for skill in skills:

            if skill not in result:
                result.append(skill)

        return result

    # =========================================================
    # EXPERIENCE
    # =========================================================

    @staticmethod
    def _extract_experience(
        text: str,
    ) -> dict:

        patterns = [
            r"(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
            r"experience\s*(?:of)?\s*(\d+)\s*\+?\s*(?:years?|yrs?)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                years = int(match.group(1))

                return {
                    "min_years": years,
                    "max_years": None,
                }

        return {
            "min_years": None,
            "max_years": None,
        }

    # =========================================================
    # EDUCATION
    # =========================================================

    @staticmethod
    def _extract_education(
        text: str,
    ) -> list[str]:

        education_keywords = (
            "bachelor",
            "master",
            "b.tech",
            "m.tech",
            "bca",
            "mca",
            "b.sc",
            "m.sc",
            "degree",
            "computer science",
            "engineering",
        )

        result = []

        for line in text.splitlines():

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in education_keywords
            ):

                clean = line.strip()

                if clean and clean not in result:
                    result.append(clean)

        return result

    # =========================================================
    # RESPONSIBILITIES
    # =========================================================

    @staticmethod
    def _extract_responsibilities(
        text: str,
    ) -> list[str]:

        section = JobDescriptionAnalyzer._extract_section(
            text,
            (
                "responsibilities",
                "roles and responsibilities",
                "what you will do",
                "what you'll do",
                "job responsibilities",
            ),
        )

        if not section:
            return []

        result = []

        for line in section.splitlines():

            line = re.sub(
                r"^[•\-\*\▪\◦]+\s*",
                "",
                line.strip(),
            )

            if line and line not in result:
                result.append(line)

        return result

    # =========================================================
    # SECTION EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_section(
        text: str,
        headers: tuple[str, ...],
    ) -> str | None:

        lines = text.splitlines()

        current = False
        collected = []

        for line in lines:

            clean = line.strip()

            lower = clean.lower().rstrip(":")

            if lower in headers:

                current = True
                continue

            if current:

                # Stop at another likely section heading.
                if (
                    clean
                    and not clean.startswith(
                        ("-", "*", "•", "▪", "◦")
                    )
                    and clean.lower().rstrip(":")
                    in {
                        "responsibilities",
                        "requirements",
                        "required skills",
                        "preferred skills",
                        "qualifications",
                        "education",
                        "experience",
                        "about the role",
                        "about us",
                    }
                ):
                    break

                collected.append(clean)

        if not collected:
            return None

        return "\n".join(collected)


job_description_analyzer = JobDescriptionAnalyzer()