import re


SKILL_ALIASES = {
    # React
    "react": "React.js",
    "reactjs": "React.js",
    "react js": "React.js",
    "react.js": "React.js",

    # Node
    "node": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node.js": "Node.js",

    # Express
    "express": "Express.js",
    "expressjs": "Express.js",
    "express js": "Express.js",
    "express.js": "Express.js",

    # PostgreSQL
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgres sql": "PostgreSQL",

    # JavaScript
    "javascript": "JavaScript",
    "java script": "JavaScript",

    # TypeScript
    "typescript": "TypeScript",
    "type script": "TypeScript",

    # Python
    "python": "Python",
    "python 3": "Python",

    # FastAPI
    "fastapi": "FastAPI",

    # REST API
    "restapi": "REST API",
    "restapis": "REST API",
    "restfulapi": "REST API",
    "restfulapis": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    # Django
    "django": "Django",

    # Angular
    "angular": "Angular",

    # HTML
    "html": "HTML",
    "html5": "HTML5",
    "html 5": "HTML5",

    # CSS
    "css": "CSS",
    "css3": "CSS3",
    "css 3": "CSS3",

    # Tailwind
    "tailwind": "TailwindCSS",
    "tailwindcss": "TailwindCSS",

    # REST APIs
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    # Authentication / backend
    "jwt": "JWT",
    "json web token": "JWT",
    "middleware": "Middleware",

    "role based access control": "Role-Based Access Control",
    "role-based access control": "Role-Based Access Control",

    # Databases
    "mysql": "MySQL",
    "sql": "SQL",

    # Cloud
    "aws": "AWS",
    "amazon web services": "AWS",

    "azure": "Azure",
    "microsoft azure": "Azure",

    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",

    # Data / AI
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv": "OpenCV",
    "open cv": "OpenCV",

    # DevOps
    "docker": "Docker",
    "kubernetes": "Kubernetes",

    # Tools
    "git": "Git",
    "github": "GitHub",
    "postman": "Postman",

    # Other
    "etl": "ETL",
    "face_recognition": "face_recognition",
    "redis": "Redis",
}


def normalize_skill_name(
    skill: str,
) -> str | None:

    skill = skill.strip()

    if not skill:
        return None

    normalized_key = re.sub(
        r"\s+",
        " ",
        skill.lower(),
    )

    normalized_key = normalized_key.strip(
        ".,;:|()[]{}"
    )

    return SKILL_ALIASES.get(
        normalized_key,
        skill.strip(),
    )


def normalize_skills(
    skills: list[str],
) -> list[str]:

    result: list[str] = []
    seen: set[str] = set()

    for skill in skills:

        normalized = normalize_skill_name(
            skill
        )

        if not normalized:
            continue

        key = normalized.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(normalized)

    return result