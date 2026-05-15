from openai import OpenAI
from config import get_api_base, get_model


ARCHITECT_SYSTEM_PROMPT = """You are an expert software architect. Given a project plan, design the complete system architecture and file structure.

Architecture principles:
- Choose the right tools for the job based on project requirements
- Follow industry best practices and established patterns
- Design for maintainability, scalability, and testability
- Include proper error handling and logging
- Separate concerns clearly (MVC, layered architecture, etc.)
- Include configuration management, environment handling
- Add proper project metadata (README, requirements, .gitignore)

Output format:
# Architecture Design

## Tech Stack
[Complete list of technologies and versions]

## Directory Structure
```
project/
  src/
    ...
  tests/
    ...
  config/
    ...
  requirements.txt
  README.md
```

## Configuration Files
[List all config files with their content purpose]

## Key Design Decisions
[Explain major architectural choices]

## Dependencies
[List all external dependencies]
"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def architect(description: str, plan: str) -> str:
    """Design the system architecture and file structure."""
    client = create_client()

    prompt = f"""Project description: {description}

Project plan:

{plan}

Design the complete architecture and file structure."""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=2500,
    )

    return response.choices[0].message.content
