# Agentic Coding Assistant

Multi-agent system that transforms natural language descriptions into complete, production-ready codebases. Built with LangGraph orchestration and 4 specialized AI agents.

## Architecture

```
┌──────────┐    ┌──────────┐    ┌───────┐    ┌──────────┐
│  Planner │───▶│ Architect│───▶│ Coder │───▶│ Reviewer │
│          │    │          │    │       │    │          │
│ Breaks   │    │ Designs  │    │ Writes│    │ Reviews  │
│ down     │    │ structure│    │ code  │    │ quality  │
│ reqs     │    │ & stack  │    │ files │    │ + README │
└──────────┘    └──────────┘    └───────┘    └──────────┘
```

**Built with:**
- **LangGraph** - State machine orchestration
- **LangChain** - LLM abstraction
- **llama.cpp** - Local model inference (Qwen 3.6 27B)
- **OpenAI API** - Optional cloud fallback

## Agents

### 1. Planner
Analyzes natural language requirements, identifies features, defines data models, API contracts, and creates a step-by-step implementation plan.

### 2. Architect
Selects optimal tech stack, designs directory structure, defines configuration, and makes key architectural decisions.

### 3. Coder
Generates complete, production-quality code for every file. Includes error handling, type hints, docstrings, and best practices.

### 4. Reviewer
Reviews code against the original plan, scores quality, identifies issues, and generates a comprehensive README.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env

# Build from description
python main.py "REST API for task management with auth"

# Specify tech stack
python main.py "URL shortener with analytics" --stack Python/FastAPI/Redis

# Demo mode
python main.py --demo

# List sample prompts
python main.py --list-prompts
```

## Output

Generated project saved to `./output/` with:
- All source code files
- `README.md` with setup instructions
- `CODE_REVIEW.md` with quality assessment
- Proper directory structure

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLAMA_SERVER_URL` | `http://172.28.176.1:11434` | Local llama.cpp server |
| `MODEL_NAME` | `qwen3.6-27b` | Model ID |
| `OPENAI_API_KEY` | *(empty)* | Set to use GPT-4o |
| `OUTPUT_DIR` | `./output` | Project output directory |

## Pipeline State

```python
class AgentState(TypedDict):
    description: str    # Natural language request
    tech_stack: str     # Preferred technologies
    plan: str           # Planner output
    architecture: str   # Architect output
    raw_code: str       # Coder output (all files)
    files: dict         # Parsed {path: content}
    review: str         # Reviewer assessment
    readme: str         # Generated README
    phase: str          # Current stage
    iterations: int     # Steps executed
```

## Example

```
$ python main.py "A web scraper for product data"

╭─ PLANNER AGENT ─╮
 Breaking down requirements...
╰ [green]Done ╯

╭─ ARCHITECT AGENT ─╮
 Designing system architecture...
╰ [green]Done ╯

╭─ CODER AGENT ─╮
 Generating production code...
╰ [green]Generated 8 files ╯

╭─ REVIEWER AGENT ─╮
 Reviewing code quality...
╰ [green]Done ╯

Project saved to: ./output/a-web-scraper-for-product-data/
```

## Use Cases

- **Rapid Prototyping** - Turn ideas into working code in minutes
- **Boilerplate Generation** - Standard project scaffolding
- **Learning** - See how experienced architects structure applications
- **Interview Prep** - Practice system design with AI pair programmer

## Extending

Add agents by creating modules in `agents/` and wiring them into the pipeline in `orchestrator.py`:

```python
def tester_node(state: AgentState) -> AgentState:
    tests = tester.generate(state["files"], state["plan"])
    return {**state, "tests": tests}

workflow.add_node("tester", tester_node)
workflow.add_edge("reviewer", "tester")
workflow.add_edge("tester", END)
```

## License

MIT
