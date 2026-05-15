from openai import OpenAI
from config import get_api_base, get_model


PLANNER_SYSTEM_PROMPT = """You are a software project planner. Given a description, produce a concise plan.

Output as a concise markdown document with:
- Overview (2-3 sentences)
- Features (bulleted list)
- Key data models
- API endpoints if applicable
- Implementation order (numbered)"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def plan(description: str, tech_stack: str = "", max_retries: int = 2) -> str:
    """Create a concise implementation plan."""
    client = create_client()

    prompt = f"Build: {description}\n{'Tech stack: ' + tech_stack if tech_stack else ''}\n\nProduce a concise implementation plan."

    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            seed=42,
        )
        content = response.choices[0].message.content
        if content and len(content) > 50:
            return content
    return content
