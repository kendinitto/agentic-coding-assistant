from openai import OpenAI
from config import get_api_base, get_model


REVIEWER_SYSTEM_PROMPT = """You are a code reviewer. Given a project description and list of generated files, write a brief assessment.

Output format:
Score: X/10
Summary: [one line]
Strengths: [2-3 bullets]
Issues: [2-3 bullets]
Recommendations: [2-3 bullets]"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def review(description: str, files: dict[str, str]) -> str:
    """Review generated files and produce assessment."""
    client = create_client()

    file_list = "\n".join(f"  {p} ({len(c)} chars)" for p, c in files.items())
    prompt = f"Project: {description}\n\nFiles:\n{file_list}\n\nReview."

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
        seed=42,
    )

    return response.choices[0].message.content.strip()
