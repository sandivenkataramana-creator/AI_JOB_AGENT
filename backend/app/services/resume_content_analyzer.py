import re


TECHNICAL_PATTERNS = [
    r"\bpython\b",
    r"\bjava\b",
    r"\bjavascript\b",
    r"\btypescript\b",
    r"\breact(?:\.js|js)?\b",
    r"\bangular\b",
    r"\bvue(?:\.js|js)?\b",
    r"\bnode(?:\.js|js)?\b",
    r"\bexpress(?:\.js|js)?\b",
    r"\bfastapi\b",
    r"\bdjango\b",
    r"\bspring\s*boot\b",
    r"\bmysql\b",
    r"\bpostgres(?:ql)?\b",
    r"\bmongodb\b",
    r"\bsql\b",
    r"\baws\b",
    r"\bazure\b",
    r"\bgcp\b",
    r"\bdocker\b",
    r"\bkubernetes\b",
    r"\bgit\b",
    r"\bpandas\b",
    r"\bnumpy\b",
    r"\bopencv\b",
    r"\btensorflow\b",
    r"\bpytorch\b",
]


EXPERIENCE_PATTERNS = [
    r"\bsoftware engineer\b",
    r"\bsoftware developer\b",
    r"\bfull[\s-]?stack developer\b",
    r"\bbackend developer\b",
    r"\bfrontend developer\b",
    r"\bweb developer\b",
    r"\bdata analyst\b",
    r"\bdata scientist\b",
    r"\bdevops engineer\b",
    r"\bdeveloper\b",
    r"\bengineer\b",
    r"\banalyst\b",
]

EDUCATION_PATTERNS = [
    r"\bMCA\b",
    r"\bMBA\b",
    r"\bBCA\b",
    r"\bB\.?TECH\b",
    r"\bB\.?E\b",
    r"\bM\.?TECH\b",
    r"\bM\.?E\b",
    r"\bB\.?SC\b",
    r"\bM\.?SC\b",
    r"\bBACHELOR\b",
    r"\bMASTER\b",
    r"\bDEGREE\b",
    r"\bUNIVERSITY\b",
    r"\bCOLLEGE\b",
    r"\bINSTITUTE\b",
    r"\bCGPA\b",
    r"\bGPA\b",
    r"\bEDUCATION\b",
]

PROJECT_PATTERNS = [
    r"\bPROJECT\b",
    r"\bPROJECTS\b",
    r"\bPERSONAL PROJECT\b",
    r"\bACADEMIC PROJECT\b",
    r"\bPROFESSIONAL PROJECT\b",
    r"\bFINAL YEAR PROJECT\b",
    r"\bCAPSTONE PROJECT\b",
]

CERTIFICATION_PATTERNS = [
    r"\bCERTIFICATE\b",
    r"\bCERTIFICATES\b",
    r"\bCERTIFIED\b",
    r"\bLICENSE\b",
    r"\bLICENSES\b",
]

DATE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b"
    r"(?:\s*[-–—]\s*"
    r"(?:\b(?:19|20)\d{2}\b|present|current))?",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text.strip()


def detect_technical_content(
    text: str,
) -> list[str]:
    """
    Detect technical terms anywhere in the resume.

    This is only a fallback detector.

    It does not replace the main section parser.
    """

    found: list[str] = []

    for pattern in TECHNICAL_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE,
        )

        if matches:
            value = matches[0]

            if value.lower() not in {
                item.lower()
                for item in found
            }:
                found.append(value)

    return found


def detect_experience_content(
    text: str,
) -> list[str]:
    """
    Detect experience-related content when a resume does not
    contain a recognizable EXPERIENCE section heading.

    Captures:
    - Job titles
    - Company/organization lines near job titles
    - Employment dates
    - Description/bullet lines associated with experience
    """

    lines = [
        line.strip()
        for line in normalize_text(text).splitlines()
        if line.strip()
    ]

    detected: list[str] = []

    experience_started = False
    consecutive_non_experience = 0

    for index, line in enumerate(lines):

        has_role = any(
            re.search(
                pattern,
                line,
                re.IGNORECASE,
            )
            for pattern in EXPERIENCE_PATTERNS
        )

        has_date = bool(
            DATE_PATTERN.search(line)
        )

        # Typical experience indicators.
        if has_role or has_date:
            experience_started = True
            consecutive_non_experience = 0

            if line not in detected:
                detected.append(line)

            continue

        if not experience_started:
            continue

        # Capture bullets/descriptions after an experience line.
        if (
            line.startswith(("•", "-", "–", "*"))
            or len(line.split()) >= 5
        ):
            detected.append(line)
            consecutive_non_experience = 0
            continue

        consecutive_non_experience += 1

        # Stop fallback experience collection after several
        # unrelated short lines.
        if consecutive_non_experience >= 3:
            break

    return detected
def detect_content_by_patterns(
    text: str,
    patterns: list[str],
) -> list[str]:
    """
    Detect potentially relevant resume content when a
    recognizable section heading is unavailable.
    """

    lines = [
        line.strip()
        for line in normalize_text(text).splitlines()
        if line.strip()
    ]

    detected: list[str] = []

    for line in lines:
        for pattern in patterns:
            if re.search(
                pattern,
                line,
                re.IGNORECASE,
            ):
                if line not in detected:
                    detected.append(line)

                break

    return detected

def analyze_resume_content(text: str) -> dict:
    """
    Analyze resume content for technical skills,
    experience, education, projects and certifications.
    """

    technical_content = detect_technical_content(text)

    experience_content = detect_experience_content(text)

    education_content = detect_content_by_patterns(
        text,
        EDUCATION_PATTERNS,
    )

    project_content = detect_content_by_patterns(
        text,
        PROJECT_PATTERNS,
    )

    certification_content = detect_content_by_patterns(
        text,
        CERTIFICATION_PATTERNS,
    )

    return {
        "technical_content": technical_content,
        "experience_content": experience_content,
        "education_content": education_content,
        "project_content": project_content,
        "certification_content": certification_content,
    }