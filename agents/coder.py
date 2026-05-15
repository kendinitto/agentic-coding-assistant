import re
from openai import OpenAI
from config import get_api_base, get_model


CODER_SYSTEM_PROMPT = """You are an expert full-stack developer. Generate complete, production-quality code.

CRITICAL OUTPUT FORMAT - follow exactly:

FILE: path/to/file.ext
[complete file contents - no markdown, no code fences, just raw code]

FILE: path/to/another/file.ext
[complete file contents]

Rules:
- Each file starts with "FILE:" followed by the path
- Then the raw file contents immediately on the next line
- No markdown backticks, no "code starts/ends" markers
- No blank lines between FILE: and the code
- Generate ALL files needed

Coding standards:
- Clean, documented, production-quality code
- Error handling, type hints, docstrings
- Follow language conventions"""


def create_client():
    api_base = get_api_base()
    if api_base.startswith("https://api.openai.com"):
        return OpenAI(api_base=api_base)
    return OpenAI(api_key="dummy", base_url=api_base)


def code(description: str, plan: str, architecture: str) -> str:
    """Generate complete code for all project files."""
    client = create_client()

    prompt = f"""Project: {description}

Plan:
{plan}

Architecture:
{architecture}

Generate ALL files. Each starts with "FILE: path" on its own line, then the raw contents immediately."""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": CODER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=4000,
    )

    return response.choices[0].message.content


def extract_files(code_output: str) -> dict[str, str]:
    """Parse code output into {filepath: content} dict. Handles multiple formats."""
    files = {}
    lines = code_output.split("\n")
    current_file = None
    current_lines = []

    skip_markers = {"<code starts here>", "<code ends here>", "```", "---"}

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("FILE:") and not stripped.startswith("FILE:  "):
            if current_file:
                content = "\n".join(current_lines).strip()
                content = re.sub(r'<code\s+(starts|ends)\s+here>\s*', '', content, flags=re.IGNORECASE)
                content = content.strip()
                if content:
                    files[current_file] = content
            current_file = stripped[5:].strip()
            current_lines = []
        elif current_file is not None:
            current_lines.append(line)

    if current_file:
        content = "\n".join(current_lines).strip()
        content = re.sub(r'<code\s+(starts|ends)\s+here>\s*', '', content, flags=re.IGNORECASE)
        content = content.strip()
        if content:
            files[current_file] = content

    return files
