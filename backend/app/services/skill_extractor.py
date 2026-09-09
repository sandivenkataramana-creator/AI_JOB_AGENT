import re

from app.services.skill_normalizer import normalize_skills


SKILL_PATTERNS = [
    "python",
    "java",
    "javascript",
    "typescript",

    "react",
    "react.js",
    "reactjs",
    "react js",

    "angular",
    "vue",

    "html",
    "html5",
    "css",
    "css3",
    "tailwindcss",

    "node",
    "node.js",
    "nodejs",

    "express",
    "express.js",
    "expressjs",

    "rest api",
    "rest apis",
    "restful api",
    "restful apis",
    "restapi",
    "restapis",
    "restfulapi",
    "restfulapis",

    "jwt",
    "middleware",
    "role based access control",
    "role-based access control",

    "mysql",
    "postgres",
    "postgresql",
    "sql",

    "pandas",
    "numpy",
    "etl",

    "opencv",
    "face_recognition",

    "git",
    "github",
    "postman",

    "docker",
    "kubernetes",
    "fastapi",
    "redis",

    "aws",
    "azure",
    "gcp",
]


def extract_skills_from_text(
    text: str,
) -> list[str]:
    """
    Extract known technical skills from resume text.

    Matching is case-insensitive.
    Duplicate skills are removed.
    Returned skills are normalized to canonical names.
    """

    found: list[str] = []

    normalized_text = text.lower()

    for skill in SKILL_PATTERNS:

        pattern = re.escape(skill)

        if re.search(
            rf"(?<![a-z0-9]){pattern}(?![a-z0-9])",
            normalized_text,
            re.IGNORECASE,
        ):
            found.append(skill)

    return normalize_skills(found)