import re

from app.services.skill_extractor import extract_skills_from_text


class ResumeIntelligenceService:

    def analyze_profile(self, profile) -> dict:
        """
        Convert a ResumeProfile into structured resume intelligence.

        This service does not modify the database.
        """

        return {
            "resume_id": profile.resume_id,

            "candidate": {
                "full_name": profile.full_name,
                "email": profile.email,
                "phone": profile.phone,
                "location": profile.location,
            },

            "summary": profile.summary,

            "skills": self._extract_skills(
                profile.skills
            ),

            "experience": self._analyze_experience(
                profile.experience
            ),

            "education": self._analyze_education(
                profile.education
            ),

            "projects": self._analyze_projects(
                profile.projects
            ),

            "certifications": self._analyze_certifications(
                profile.certifications
            ),
        }

    # =========================================================
    # SKILLS
    # =========================================================

    def _extract_skills(
        self,
        skills: str | None,
    ) -> list[str]:

        if not skills:
            return []

        return extract_skills_from_text(skills)

    # =========================================================
    # EXPERIENCE
    # =========================================================

    def _analyze_experience(
        self,
        experience: str | None,
    ) -> dict:

        if not experience:
            return {
                "raw_text": None,
                "entries": [],
                "technologies": [],
            }

        lines = self._clean_lines(experience)

        entries = []
        technologies = []

        current_entry = None

        for line in lines:

            header = self._parse_experience_header(line)

            if header:

                if current_entry:
                    entries.append(current_entry)

                current_entry = {
                    "company": header["company"],
                    "role": header["role"],
                    "location": header["location"],
                    "start_date": header["start_date"],
                    "end_date": header["end_date"],
                    "technologies": [],
                    "responsibilities": [],
                }

                continue

            if current_entry is None:
                continue

            # -------------------------------------------------
            # Technology extraction
            # -------------------------------------------------

            line_skills = extract_skills_from_text(line)

            for skill in line_skills:

                if skill not in current_entry["technologies"]:
                    current_entry["technologies"].append(skill)

                if skill not in technologies:
                    technologies.append(skill)

            # -------------------------------------------------
            # Tech Stack line
            # -------------------------------------------------

            if line.lower().startswith("tech stack"):

                stack_text = re.sub(
                    r"^tech stack\s*:\s*",
                    "",
                    line,
                    flags=re.IGNORECASE,
                )

                stack_skills = extract_skills_from_text(
                    stack_text
                )

                for skill in stack_skills:

                    if skill not in current_entry["technologies"]:
                        current_entry["technologies"].append(skill)

                    if skill not in technologies:
                        technologies.append(skill)

                continue

            # -------------------------------------------------
            # Responsibility / description
            # -------------------------------------------------

            if self._looks_like_responsibility(line):

                current_entry["responsibilities"].append(
                    line
                )

        if current_entry:
            entries.append(current_entry)

        return {
            "raw_text": experience,
            "entries": entries,
            "technologies": technologies,
        }

    # =========================================================
    # EXPERIENCE HEADER PARSER
    # =========================================================

    def _parse_experience_header(
        self,
        line: str,
    ) -> dict | None:

        original = line.strip()

        if not original:
            return None

        # -----------------------------------------------------
        # Find date range
        #
        # Examples:
        #
        # Oct 2025–Present
        # Oct 2025 - Present
        # 2023 - 2025
        # 2023–Present
        # -----------------------------------------------------

        date_pattern = re.compile(
            r"(?P<start>"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\.?\s+"
            r"(?:19|20)\d{2}"
            r"|"
            r"(?:19|20)\d{2}"
            r")"
            r"\s*[-–—]\s*"
            r"(?P<end>"
            r"Present"
            r"|"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\.?\s+"
            r"(?:19|20)\d{2}"
            r"|"
            r"(?:19|20)\d{2}"
            r")",
            re.IGNORECASE,
        )

        match = date_pattern.search(original)

        if not match:
            return None

        start_date = match.group("start").strip()
        end_date = match.group("end").strip()

        before_date = original[:match.start()].strip()

        # -----------------------------------------------------
        # Remove trailing separators
        # -----------------------------------------------------

        before_date = before_date.rstrip("|-–—, ")

        # -----------------------------------------------------
        # Usually:
        #
        # Software Engineer |
        # Avniya Cloud Technologies,
        # Hyderabad, India
        #
        # -----------------------------------------------------

        role = None
        company = None
        location = None

        if "|" in before_date:

            parts = [
                part.strip()
                for part in before_date.split("|")
                if part.strip()
            ]

            if len(parts) >= 2:

                role = parts[0]

                company_location = "|".join(
                    parts[1:]
                ).strip()

            else:
                company_location = before_date

        else:

            company_location = before_date

        # -----------------------------------------------------
        # Detect location
        # -----------------------------------------------------

        location_match = re.search(
            r",\s*([A-Za-z .'-]+,\s*[A-Za-z .'-]+)$",
            company_location,
        )

        if location_match:

            location = location_match.group(1).strip()

            company = company_location[
                :location_match.start()
            ].rstrip(", ")

        else:

            company = company_location.strip()

        # -----------------------------------------------------
        # If role wasn't separated with "|",
        # attempt role detection.
        # -----------------------------------------------------

        if not role:

            role_keywords = [
                "software engineer",
                "software developer",
                "full stack engineer",
                "full-stack engineer",
                "full stack developer",
                "full-stack developer",
                "backend engineer",
                "backend developer",
                "frontend engineer",
                "frontend developer",
                "data engineer",
                "data analyst",
                "data scientist",
                "devops engineer",
                "qa engineer",
                "project manager",
                "intern",
            ]

            lower_company = company.lower()

            for keyword in role_keywords:

                if lower_company.startswith(keyword):

                    role = company[
                        :len(keyword)
                    ].strip()

                    company = company[
                        len(keyword):
                    ].strip(" ,-")

                    break

        if not role:
            return None

        if not company:
            return None

        return {
            "role": role,
            "company": company,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
        }

    # =========================================================
    # RESPONSIBILITY DETECTION
    # =========================================================

    @staticmethod
    def _looks_like_responsibility(
        line: str,
    ) -> bool:

        lower = line.lower()

        responsibility_starts = (
            "built ",
            "developed ",
            "designed ",
            "implemented ",
            "created ",
            "managed ",
            "led ",
            "owned ",
            "improved ",
            "optimized ",
            "deployed ",
            "maintained ",
            "automated ",
            "collaborated ",
            "worked ",
            "delivered ",
            "engineered ",
            "performed ",
            "leveraged ",
        )

        return (
            line.startswith(("•", "-", "*"))
            or lower.startswith(
                responsibility_starts
            )
        )

    # =========================================================
    # EDUCATION
    # =========================================================

    def _analyze_education(
        self,
        education: str | None,
    ) -> dict:

        if not education:
            return {
                "raw_text": None,
                "entries": [],
            }

        lines = self._clean_lines(education)

        entries = []

        current = None

        for line in lines:

            if self._looks_like_degree(line):

                if current:
                    entries.append(current)

                current = {
                    "degree": line,
                    "institution": None,
                    "years": [],
                    "details": [],
                }

                years = self._extract_years(line)

                current["years"].extend(years)

                continue

            if current is None:
                continue

            years = self._extract_years(line)

            for year in years:

                if year not in current["years"]:
                    current["years"].append(year)

            if self._looks_like_institution(line):

                if not current["institution"]:
                    current["institution"] = line

            else:

                current["details"].append(line)

        if current:
            entries.append(current)

        return {
            "raw_text": education,
            "entries": entries,
        }

    # =========================================================
    # DEGREE DETECTION
    # =========================================================

    @staticmethod
    def _looks_like_degree(
        line: str,
    ) -> bool:

        lower = line.lower()

        keywords = [
            "bca",
            "mca",
            "btech",
            "b.tech",
            "mtech",
            "m.tech",
            "b.e",
            "be ",
            "m.e",
            "me ",
            "bachelor",
            "master",
            "mba",
            "phd",
            "doctorate",
            "diploma",
        ]

        return any(
            keyword in lower
            for keyword in keywords
        )

    # =========================================================
    # INSTITUTION DETECTION
    # =========================================================

    @staticmethod
    def _looks_like_institution(
        line: str,
    ) -> bool:

        lower = line.lower()

        keywords = [
            "university",
            "college",
            "institute",
            "school",
        ]

        return any(
            keyword in lower
            for keyword in keywords
        )

    # =========================================================
    # PROJECTS
    # =========================================================

    def _analyze_projects(
        self,
        projects: str | None,
    ) -> dict:

        if not projects:
            return {
                "raw_text": None,
                "entries": [],
                "technologies": [],
            }

        lines = self._clean_lines(projects)

        entries = []
        current = None

        for line in lines:
            if self._looks_like_project_title(line):
                if current is not None:
                    entries.append(current)

                current = {
                    "name": self._clean_project_name(line),
                    "technologies": [],
                    "description": [],
                }

                title_skills = extract_skills_from_text(line)

                for skill in title_skills:
                    if skill not in current["technologies"]:
                        current["technologies"].append(skill)

                continue

            if current is None:
                continue

            clean_line = self._remove_bullet(line)

            if not clean_line:
                continue

            line_skills = extract_skills_from_text(clean_line)

            for skill in line_skills:
                if skill not in current["technologies"]:
                    current["technologies"].append(skill)

            current["description"].append(clean_line)

        if current is not None:
            entries.append(current)

        technologies = []

        for entry in entries:
            for skill in entry["technologies"]:
                if skill not in technologies:
                    technologies.append(skill)

        return {
            "raw_text": projects,
            "entries": entries,
            "technologies": technologies,
        }

    # =========================================================
    # PROJECT TITLE DETECTION
    # =========================================================

    def _looks_like_project_title(
        self,
        line: str,
    ) -> bool:

        if not line.strip():
            return False

        if line.startswith(("•", "-", "*", "▪", "●")):
            return False

        clean = self._remove_bullet(line)

        if not clean:
            return False

        lower = clean.lower()

        # ---------------------------------------------------------
        # Reject description-like lines and technical stack lines.
        # ---------------------------------------------------------
        technical_prefixes = (
            "tech stack",
            "languages",
            "frontend",
            "backend",
            "backend/apis",
            "databases",
            "data analytics",
            "ai/computer vision",
            "tools",
            "tools & practices",
            "technologies",
        )

        if lower.startswith(technical_prefixes):
            return False

        continuation_starts = (
            "management",
            "order",
            "cart",
            "schema",
            "achieving",
            "secured",
            "handled",
            "built",
            "developed",
            "implemented",
            "designed",
            "created",
            "used",
            "using",
            "with ",
            "and ",
            "or ",
            "the ",
            "this ",
            "that ",
            "from ",
            "into ",
            "across ",
            "for ",
            "production ",
            "operational ",
            "automated ",
            "performed ",
            "wrote ",
            "delivered ",
        )

        if lower.startswith(continuation_starts):
            return False

        if clean.endswith((".", ",", ";", ":")):
            return False

        cleaned_title = self._clean_project_name(clean)
        if not cleaned_title:
            return False

        cleaned_lower = cleaned_title.lower()
        title_words = cleaned_title.split()

        # ---------------------------------------------------------
        # Strong project-name indicators
        # ---------------------------------------------------------
        project_indicators = (
            "application",
            "system",
            "portal",
            "platform",
            "website",
            "dashboard",
            "e-commerce",
            "ecommerce",
            "face recognition",
            "attendance",
            "management system",
        )

        if any(indicator in cleaned_lower for indicator in project_indicators):
            return True

        # ---------------------------------------------------------
        # If technologies were removed, the original line was
        # probably a project title followed by a technology stack.
        # ---------------------------------------------------------
        if cleaned_title != clean:
            if len(title_words) <= 10:
                return True

        # ---------------------------------------------------------
        # Reject genuinely long description lines.
        # ---------------------------------------------------------
        if len(title_words) > 10:
            return False

        # ---------------------------------------------------------
        # Short title heuristic
        # ---------------------------------------------------------
        if len(title_words) <= 7:
            capitalized_words = sum(
                1 for word in title_words if word[:1].isupper()
            )
            return capitalized_words >= max(1, len(title_words) // 2)

        return False

    # =========================================================
    # CERTIFICATIONS
    # =========================================================

    def _analyze_certifications(
        self,
        certifications: str | None,
    ) -> list[str]:

        if not certifications:
            return []

        return [
            self._remove_bullet(line)
            for line in certifications.splitlines()
            if line.strip()
        ]

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _clean_lines(
        text: str,
    ) -> list[str]:

        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    @staticmethod
    def _remove_bullet(
        text: str,
    ) -> str:

        return re.sub(
            r"^[•▪●\-\*]+\s*",
            "",
            text.strip(),
        ).strip()

    @staticmethod
    def _clean_project_name(
        text: str,
    ) -> str:

        text = text.strip()

        if not text:
            return ""

        technology_pattern = re.compile(
            r"\s+(?:"
            r"React\.js|ReactJS|"
            r"Node\.js|NodeJS|"
            r"Express\.js|ExpressJS|"
            r"Python|"
            r"Angular|"
            r"Java|"
            r"JavaScript|"
            r"TypeScript|"
            r"MySQL|"
            r"PostgreSQL|"
            r"MongoDB|"
            r"FastAPI|"
            r"Django|"
            r"AWS|"
            r"Docker|"
            r"OpenCV|"
            r"Pandas|"
            r"JWT|"
            r"RESTAPIs?|"
            r"RESTful\s+APIs?"
            r")(?:\s|$)",
            re.IGNORECASE,
        )

        match = technology_pattern.search(text)

        if match:
            text = text[:match.start()]

        return text.strip(" -–—·|").strip()

    @staticmethod
    def _extract_years(
        text: str,
    ) -> list[str]:

        return re.findall(
            r"\b(?:19|20)\d{2}\b",
            text,
        )


resume_intelligence_service = ResumeIntelligenceService()