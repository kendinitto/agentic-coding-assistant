from openai import OpenAI
from config import get_api_base, get_model


CODER_SYSTEM_PROMPT = """You are an expert developer. Generate complete, production-quality code for a single file.

Rules:
- Write the COMPLETE file contents
- Include imports, error handling, docstrings
- Follow best practices and conventions for the language
- Output ONLY the raw code, no explanations, no markdown fences
- The code should be ready to run"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def generate_file(filepath: str, purpose: str, language: str, description: str, plan: str) -> str:
    """Generate a single file's code."""
    client = create_client()

    prompt = f"""Generate the complete code for this file:

File: {filepath}
Language: {language}
Purpose: {purpose}

Project context: {description}

Plan summary:
{plan[:800]}

Output ONLY the raw code for {filepath}. No explanations, no markdown."""

    for attempt in range(3):
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": CODER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            seed=42,
        )
        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            content = "\n".join(lines).strip()

        if content and len(content) > 10:
            return content

    return content


def generate_all_files(files: list[dict], description: str, plan: str) -> dict[str, str]:
    """Generate code for all files. Returns {path: content}."""
    result = {}
    total = len(files)

    for i, file_info in enumerate(files, 1):
        filepath = file_info["path"]
        purpose = file_info.get("purpose", "")
        language = file_info.get("language", "unknown")

        print(f"  [{i}/{total}] Generating: {filepath}")

        content = generate_file(filepath, purpose, language, description, plan)
        result[filepath] = content

    return result
