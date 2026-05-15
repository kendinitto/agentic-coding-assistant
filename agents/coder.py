import ast
import re
from openai import OpenAI
from config import get_api_base, get_model


CODER_SYSTEM_PROMPT = """You are an expert developer. Generate complete, production-quality code for a single file.

Rules:
- Write COMPLETE, working code
- Keep it concise - prioritize working code over length
- Include error handling and docstrings
- Output ONLY raw code, no explanations, no markdown"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def truncate_to_valid_python(code: str) -> str:
    """If code is truncated mid-statement, trim to last valid line."""
    # Try to parse as-is
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass

    # Remove markdown code fences
    code = re.sub(r'```[\w]*\n?', '', code).strip()

    # Try again
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass

    # Trim line by line from the end until valid
    lines = code.split("\n")
    # Keep trimming from end
    for i in range(len(lines), 0, -1):
        trimmed = "\n".join(lines[:i])
        try:
            ast.parse(trimmed)
            return trimmed
        except SyntaxError:
            continue

    # If still invalid, try removing last incomplete function/class
    # Find last def/class and keep everything before it
    pattern = r'\n(def |class )'
    last_match = 0
    for m in re.finditer(pattern, code):
        last_match = m.start()

    if last_match > 0:
        trimmed = code[:last_match].rstrip()
        try:
            ast.parse(trimmed)
            return trimmed
        except SyntaxError:
            pass

    return code


def generate_file(filepath: str, purpose: str, language: str, description: str, plan: str) -> str:
    """Generate a single file's code."""
    client = create_client()

    prompt = f"""Generate complete code for {filepath}.
Language: {language}
Purpose: {purpose}
Project: {description}

Plan:
{plan[:600]}

Write concise, working code. Output ONLY the code."""

    for attempt in range(3):
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": CODER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=3000,
            seed=42,
        )
        content = response.choices[0].message.content.strip()

        # Strip markdown fences
        if content.startswith("```"):
            content = re.sub(r'```[\w]*\n?', '', content).strip()

        if content and len(content) > 10:
            # Ensure valid Python for .py files
            if filepath.endswith(".py"):
                content = truncate_to_valid_python(content)
            return content

    return ""


def generate_all_files(files: list[dict], description: str, plan: str) -> dict[str, str]:
    """Generate code for all files."""
    result = {}
    total = len(files)

    for i, file_info in enumerate(files, 1):
        filepath = file_info["path"]
        purpose = file_info.get("purpose", "")
        language = file_info.get("language", "unknown")

        print(f"  [{i}/{total}] Generating: {filepath}")
        content = generate_file(filepath, purpose, language, description, plan)
        if content:
            result[filepath] = content
            print(f"    OK ({len(content)} chars)")
        else:
            print(f"    FAILED")

    return result
