from openai import OpenAI
from config import get_api_base, get_model


ARCHITECT_SYSTEM_PROMPT = """Design file structure for a project. List each file on its own line in format:
path :: purpose :: language

Example:
main.py :: CLI entry point with argument parsing :: python
db.py :: Database models and queries :: python
requirements.txt :: Python package dependencies :: text"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def architect(description: str, plan: str, max_retries: int = 3) -> list[dict]:
    """Design file structure."""
    client = create_client()

    plan_lines = plan.strip().split("\n")[:15]
    plan_summary = "\n".join(plan_lines)

    prompt = f"""Project: {description}

Plan:
{plan_summary}

List all files needed, one per line:"""

    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            seed=42,
        )
        content = response.choices[0].message.content.strip()

        if not content:
            continue

        files = []
        for line in content.split("\n"):
            line = line.strip()
            if "::" in line and not line.startswith("#") and not line.startswith("-"):
                parts = [p.strip() for p in line.split("::")]
                if len(parts) >= 2 and parts[0]:
                    files.append({
                        "path": parts[0],
                        "purpose": parts[1],
                        "language": parts[2] if len(parts) > 2 else "unknown",
                    })

        if files:
            return files

    return [
        {"path": "main.py", "purpose": "Main entry point", "language": "python"},
        {"path": "requirements.txt", "purpose": "Dependencies", "language": "text"},
        {"path": "README.md", "purpose": "Documentation", "language": "markdown"},
    ]
