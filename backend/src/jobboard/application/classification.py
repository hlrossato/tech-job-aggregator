import re

TECHNOLOGY_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python", "django", "fastapi", "flask"),
    "JavaScript": ("javascript", "typescript", "node.js", "nodejs"),
    "React": ("react", "next.js", "nextjs"),
    "C#": ("c#", ".net", "dotnet", "asp.net"),
    "Java": ("java", "spring boot", "spring"),
    "Go": ("golang", "go developer"),
    "Rust": ("rust",),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure",),
    "GCP": ("gcp", "google cloud"),
    "Docker": ("docker", "containerization"),
    "Kubernetes": ("kubernetes", "k8s"),
    "Terraform": ("terraform", "infrastructure as code"),
    "PostgreSQL": ("postgresql", "postgres"),
    "Spark": ("apache spark", "pyspark"),
    "Airflow": ("airflow",),
    "dbt": ("dbt",),
}

SENIORITY_ALIASES: dict[str, tuple[str, ...]] = {
    "junior": ("junior", "jr", "entry-level", "entry level", "estagiário", "intern"),
    "mid": ("mid-level", "mid level", "pleno"),
    "senior": ("senior", "sr "),
    "staff": ("staff",),
    "principal": ("principal", "distinguished"),
}

ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "software-engineering": ("software engineer", "developer", "programador", "desenvolvedor"),
    "devops-sre": ("devops", "site reliability", "sre", "platform engineer"),
    "cloud": ("cloud engineer", "cloud architect", "engenheiro de cloud"),
    "data": ("data engineer", "data scientist", "analytics engineer", "engenheiro de dados"),
    "security": ("security engineer", "cybersecurity", "application security", "segurança"),
    "qa": ("qa engineer", "quality assurance", "test engineer", "sdet"),
    "infrastructure": ("infrastructure engineer", "systems engineer", "network engineer"),
    "product-engineering": ("product engineer", "technical product"),
    "technical-support": ("support engineer", "technical support", "customer engineer"),
}


def _contains(text: str, alias: str) -> bool:
    return re.search(rf"(?<![\w+#]){re.escape(alias)}(?![\w+#])", text, re.IGNORECASE) is not None


class RuleBasedTechnologyClassifier:
    def classify(self, title: str, description: str) -> tuple[tuple[str, ...], str | None, float]:
        text = f"{title}\n{description}"
        technologies = tuple(
            technology
            for technology, aliases in TECHNOLOGY_ALIASES.items()
            if any(_contains(text, alias) for alias in aliases)
        )

        title_folded = title.casefold()
        role_scores = {
            role: sum(
                3 if _contains(title_folded, alias) else 1 if _contains(text, alias) else 0
                for alias in aliases
            )
            for role, aliases in ROLE_ALIASES.items()
        }
        scored = any(role_scores.values())
        role_category = max(role_scores, key=lambda role: role_scores[role]) if scored else None
        role_points = (role_scores[role_category] if role_category else 0) * 0.2
        confidence = min(1.0, role_points + (len(technologies) * 0.08))
        return technologies, role_category, confidence


def detect_seniority(title: str) -> str | None:
    folded = f" {title.casefold()} "
    for seniority, aliases in SENIORITY_ALIASES.items():
        if any(alias in folded for alias in aliases):
            return seniority
    return None
