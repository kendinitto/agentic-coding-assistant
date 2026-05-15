from openai import OpenAI
from config import get_api_base, get_model


REVIEWER_SYSTEM_PROMPT = """You are an expert code reviewer and technical writer. Given the project details, generate a concise code review AND a README.md.

Output format:

## Code Review
Score: X/10
Summary: [one line]
Strengths: [bullets]
Issues: [bullets]

## README
# Project Name
[description]

## Installation
[instructions]

## Usage
[examples]
"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def review(description: str, plan: str, files: dict[str, str]) -> str:
    """Review generated files and produce assessment."""
    client = create_client()

    file_summary = "\n".join(f"  {p}: {len(c)} chars" for p, c in files.items())

    prompt = f"""Project: {description}

Files generated ({len(files)}):
{file_summary}

Generate a code review and README."""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=2000,
    )

    return response.choices[0].message.content
