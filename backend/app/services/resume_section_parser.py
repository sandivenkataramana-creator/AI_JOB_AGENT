import re

from app.services.resume_content_analyzer import analyze_resume_content

SECTION_HEADERS = {
    "summary": [
        "PROFESSIONAL SUMMARY",
        "PROFESSIONAL PROFILE",
        "CAREER SUMMARY",
        "CAREER PROFILE",
        "EXECUTIVE SUMMARY",
        "SUMMARY",
        "PROFILE",
        "ABOUT ME",
        "ABOUT",
        "OBJECTIVE",
        "CAREER OBJECTIVE",
        "PROFESSIONAL OBJECTIVE",
    ],

    "skills": [
        "TECHNICAL SKILLS",
        "TECHNICAL EXPERTISE",
        "TECHNOLOGIES",
        "TECHNOLOGY",
        "CORE SKILLS",
        "CORE COMPETENCIES",
        "KEY SKILLS",
        "SKILL SET",
        "SKILLS",
        "TECHNOLOGY STACK",
        "TECH STACK",
        "AREAS OF EXPERTISE",
        "EXPERTISE",
    ],

    "experience": [
        "PROFESSIONAL EXPERIENCE",
        "WORK EXPERIENCE",
        "WORK HISTORY",
        "EMPLOYMENT HISTORY",
        "EMPLOYMENT",
        "CAREER HISTORY",
        "PROFESSIONAL HISTORY",
        "EXPERIENCE",
    ],

    "education": [
        "EDUCATION",
        "EDUCATIONAL BACKGROUND",
        "ACADEMIC BACKGROUND",
        "ACADEMIC QUALIFICATIONS",
        "EDUCATIONAL QUALIFICATIONS",
        "ACADEMIC HISTORY",
        "QUALIFICATIONS",
    ],

    "projects": [
        "PROJECTS",
        "KEY PROJECTS",
        "PERSONAL PROJECTS",
        "ACADEMIC PROJECTS",
        "PROFESSIONAL PROJECTS",
        "SELECTED PROJECTS",
        "PROJECT EXPERIENCE",
    ],

    "certifications": [
        "CERTIFICATIONS",
        "CERTIFICATES",
        "PROFESSIONAL CERTIFICATIONS",
        "PROFESSIONAL CERTIFICATES",
        "LICENSES & CERTIFICATIONS",
        "LICENSES AND CERTIFICATIONS",
    ],
}


def normalize_text(text: str) -> str:
    """
    Normalize line endings.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text.strip()


def normalize_header(text: str) -> str:
    """
    Normalize a possible section heading.

    Examples:

        Technical Skills
        TECHNICAL SKILLS
        Technical Skills:
        TECHNICAL   SKILLS

    become:

        TECHNICAL SKILLS
    """

    text = text.strip()

    # Remove trailing punctuation
    text = re.sub(r"[:\-–—]+$", "", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.upper()


def compact_header(text: str) -> str:
    """
    Remove spaces and punctuation from a header.

    This handles PDF extraction problems such as:

        PROFESSIONAL SUMMARY
        PROFESSIONALSUMMARY

    Both become:

        PROFESSIONALSUMMARY
    """

    return re.sub(
        r"[^A-Z0-9]",
        "",
        normalize_header(text),
    )


def build_header_lookup() -> dict[str, str]:
    """
    Build lookup table for both normal and compact headers.
    """

    lookup: dict[str, str] = {}

    for section_name, headers in SECTION_HEADERS.items():

        for header in headers:

            normalized = normalize_header(header)
            compact = compact_header(header)

            lookup[normalized] = section_name
            lookup[compact] = section_name

    return lookup


HEADER_LOOKUP = build_header_lookup()


def extract_email(text: str) -> str | None:
    """
    Extract an email address.

    Works with normal emails and markdown-style extracted text.
    """

    match = re.search(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
    )

    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """
    Extract common Indian phone number formats.

    Examples:

        +919948696842
        +91 99489696842
        +91-99489696842
        99489696842
    """

    match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}\b",
        text,
    )

    return match.group(0) if match else None


def extract_location(text: str) -> str | None:
    """
    Basic location extraction.

    This is intentionally conservative for now.
    """

    patterns = [
        r"\bHyderabad,\s*India\b",
        r"\bHyderabad\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(0)

    return None


def extract_full_name(text: str) -> str | None:
    """
    Preliminary name extraction.

    Currently uses the first meaningful line.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    first_line = lines[0]

    # Don't treat a known section heading as a name.
    if (
        normalize_header(first_line) in HEADER_LOOKUP
        or compact_header(first_line) in HEADER_LOOKUP
    ):
        return None

    return first_line


def is_section_header(line: str) -> str | None:
    """
    Determine whether a line represents a known resume section.

    Supports both normal headings and headings where PDF
    extraction has removed spaces.
    """

    normalized = normalize_header(line)

    # Normal match
    section = HEADER_LOOKUP.get(normalized)

    if section:
        return section

    # Compact match
    compact = compact_header(line)

    return HEADER_LOOKUP.get(compact)


def extract_sections(text: str) -> dict[str, str]:
    """
    Extract known resume sections.
    """

    text = normalize_text(text)

    lines = text.splitlines()

    sections: dict[str, str] = {}

    current_section: str | None = None
    current_lines: list[str] = []

    for line in lines:

        detected_section = is_section_header(line)

        if detected_section:

            # Save previous section
            if current_section is not None:

                content = "\n".join(
                    current_lines
                ).strip()

                if content:
                    sections[current_section] = content

            # Start new section
            current_section = detected_section
            current_lines = []

            continue

        if current_section is not None:
            current_lines.append(line)

    # Save final section
    if current_section is not None:

        content = "\n".join(
            current_lines
        ).strip()

        if content:
            sections[current_section] = content

    return sections


def parse_resume_text(text: str) -> dict:
    """
    Parse raw resume text into a normalized profile structure.

    Section-based extraction is preferred.

    Content-based analysis is used as a fallback when
    standard section headings are missing.
    """

    text = normalize_text(text)

    # -----------------------------------------
    # 1. Primary section-based parsing
    # -----------------------------------------

    sections = extract_sections(text)

    # -----------------------------------------
    # 2. Content-based fallback analysis
    # -----------------------------------------

    content_analysis = analyze_resume_content(text)

    # -----------------------------------------
    # 3. Existing sections
    # -----------------------------------------

    summary = sections.get("summary")

    skills = sections.get("skills")

    experience = sections.get("experience")

    education = sections.get("education")

    projects = sections.get("projects")

    certifications = sections.get("certifications")

    # -----------------------------------------
    # 4. Fallback for missing skills
    # -----------------------------------------

    if not skills:

        technical_content = content_analysis.get(
            "technical_content",
            [],
        )

        if technical_content:
            skills = ", ".join(
                technical_content
            )

    # -----------------------------------------
    # 5. Fallback for missing experience
    # -----------------------------------------

    if not experience:

        experience_content = content_analysis.get(
            "experience_content",
            [],
        )

        if experience_content:
            experience = "\n".join(
                experience_content
            )

    # -----------------------------------------
    # 6. Fallback for missing education
    # -----------------------------------------

    if not education:

        education_content = content_analysis.get(
            "education_content",
            [],
        )

        if education_content:
            education = "\n".join(
                education_content
            )

    # -----------------------------------------
    # 7. Fallback for missing projects
    # -----------------------------------------

    if not projects:

        project_content = content_analysis.get(
            "project_content",
            [],
        )

        if project_content:
            projects = "\n".join(
                project_content
            )

    # -----------------------------------------
    # 8. Fallback for missing certifications
    # -----------------------------------------

    if not certifications:

        certification_content = content_analysis.get(
            "certification_content",
            [],
        )

        if certification_content:
            certifications = "\n".join(
                certification_content
            )

    # -----------------------------------------
    # 9. Return normalized profile
    # -----------------------------------------

    return {
        "full_name": extract_full_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "location": extract_location(text),

        "summary": summary,

        "skills": skills,

        "experience": experience,

        "education": education,

        "projects": projects,

        "certifications": certifications,
    }