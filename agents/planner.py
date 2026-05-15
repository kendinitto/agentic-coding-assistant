from openai import OpenAI
from config import get_api_base, get_model


PLANNER_SYSTEM_PROMPT = """You are an expert software project planner. Given a natural language description of an application, break it down into a comprehensive, actionable implementation plan.

Planning methodology:
1. Understand the core requirements and identify implicit needs
2. Define the application architecture (frontend, backend, database, APIs)
3. List all features with priority (must-have vs nice-to-have)
4. Identify all components, modules, and their relationships
5. Define data models and API contracts
6. List all files that need to be created with their purpose
7. Identify potential technical challenges and propose solutions

Output format:
# Project Plan: [Name]

## Overview
[Brief description of what the app does]

## Core Features
- [Feature 1]: [description]
- [Feature 2]: [description]

## Technical Requirements
- [Requirements]

## Data Models
- [Model descriptions]

## API Endpoints
- [Endpoint list]

## File Structure
[Complete list of files to create with brief purpose]

## Implementation Order
1. [Step 1]
2. [Step 2]
...
"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def plan(description: str, tech_stack: str = "") -> str:
    """Create a comprehensive implementation plan from a natural language description."""
    client = create_client()

    prompt = f"""I want to build: {description}
{'Preferred tech stack: ' + tech_stack if tech_stack else ''}

Create a detailed implementation plan."""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=2500,
    )

    return response.choices[0].message.content
