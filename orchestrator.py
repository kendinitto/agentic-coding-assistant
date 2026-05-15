from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents import planner, architect, coder, reviewer
from config import OUTPUT_DIR
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class AgentState(TypedDict):
    description: str
    tech_stack: str
    plan: str
    architecture: str
    raw_code: str
    files: dict
    review: str
    phase: str
    iterations: int


def plan_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold cyan]PLANNER AGENT[/bold cyan]\nBreaking down requirements...",
        border_style="cyan"
    ))
    plan_result = planner.plan(state["description"], state["tech_stack"])
    console.print("[green]Planning complete.[/green]")
    return {**state, "plan": plan_result, "phase": "planned", "iterations": state["iterations"] + 1}


def architecture_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold blue]ARCHITECT AGENT[/bold blue]\nDesigning system architecture...",
        border_style="blue"
    ))
    arch_result = architect.architect(state["description"], state["plan"])
    console.print("[green]Architecture complete.[/green]")
    return {**state, "architecture": arch_result, "phase": "architectured", "iterations": state["iterations"] + 1}


def code_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold green]CODER AGENT[/bold green]\nGenerating production code...",
        border_style="green"
    ))
    code_result = coder.code(state["description"], state["plan"], state["architecture"])
    files = coder.extract_files(code_result)
    console.print(f"[green]Generated {len(files)} files.[/green]")
    return {**state, "raw_code": code_result, "files": files, "phase": "coded", "iterations": state["iterations"] + 1}


def review_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold magenta]REVIEWER AGENT[/bold magenta]\nReviewing code quality...",
        border_style="magenta"
    ))
    review_result = reviewer.review(state["description"], state["plan"], state["files"])
    console.print("[green]Review complete.[/green]")
    return {**state, "review": review_result, "phase": "reviewed", "iterations": state["iterations"] + 1}


def save_project(state: AgentState, project_name: str) -> str:
    """Save generated project files to disk."""
    safe_name = project_name.lower().replace(" ", "-").replace("/", "-")
    project_dir = OUTPUT_DIR / safe_name
    project_dir.mkdir(parents=True, exist_ok=True)

    for filepath, content in state["files"].items():
        full_path = project_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    review_path = project_dir / "REVIEW.md"
    with open(review_path, "w") as f:
        f.write(state["review"])

    return str(project_dir)


def build_pipeline() -> StateGraph:
    """Build the multi-agent coding pipeline."""
    workflow = StateGraph(AgentState)
    workflow.add_node("planner", plan_node)
    workflow.add_node("architect", architecture_node)
    workflow.add_node("coder", code_node)
    workflow.add_node("reviewer", review_node)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "architect")
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "reviewer")
    workflow.add_edge("reviewer", END)
    return workflow


def run_pipeline(description: str, tech_stack: str = "", save_files: bool = True) -> AgentState:
    """Execute the full agentic coding pipeline."""
    console.print(Panel(
        f"[bold]Agentic Coding Assistant[/bold]\n\n"
        f"Request: {description}\n"
        f"{'Tech stack: ' + tech_stack if tech_stack else 'Tech stack: auto-select'}\n"
        f"Agents: Planner -> Architect -> Coder -> Reviewer",
        border_style="white",
        title="Pipeline",
    ))

    graph = build_pipeline()
    app = graph.compile()

    initial_state = {
        "description": description,
        "tech_stack": tech_stack,
        "plan": "",
        "architecture": "",
        "raw_code": "",
        "files": {},
        "review": "",
        "phase": "init",
        "iterations": 0,
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Agents working...", total=None)
        result = app.invoke(initial_state)
        progress.update(task, completed=True)

    if save_files and result["files"]:
        project_dir = save_project(result, description[:40])
        console.print(f"\n[bold green]Project saved to: {project_dir}[/bold green]")

    console.print(f"\n[bold green]Pipeline complete![/bold green]")
    console.print(f"Files: {len(result['files'])} | Steps: {result['iterations']}")

    return result
