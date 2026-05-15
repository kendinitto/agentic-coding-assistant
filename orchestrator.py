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
    file_list: list
    files: dict
    review: str
    phase: str
    iterations: int


def plan_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold cyan]PLANNER AGENT[/bold cyan]\nBreaking down requirements...",
        border_style="cyan"
    ))
    plan = planner.plan(state["description"], state["tech_stack"])
    console.print("[green]Planning complete.[/green]")
    return {**state, "plan": plan, "phase": "planned", "iterations": state["iterations"] + 1}


def architecture_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold blue]ARCHITECT AGENT[/bold blue]\nDesigning file structure...",
        border_style="blue"
    ))
    file_list = architect.architect(state["description"], state["plan"])
    console.print(f"[green]Designed {len(file_list)} files.[/green]")
    return {**state, "file_list": file_list, "phase": "architectured", "iterations": state["iterations"] + 1}


def code_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold green]CODER AGENT[/bold green]\nGenerating code for each file...",
        border_style="green"
    ))
    files = coder.generate_all_files(
        state["file_list"], state["description"], state["plan"]
    )
    generated = sum(1 for c in files.values() if len(c) > 10)
    console.print(f"[green]Generated {generated}/{len(files)} files successfully.[/green]")
    return {**state, "files": files, "phase": "coded", "iterations": state["iterations"] + 1}


def review_node(state: AgentState) -> AgentState:
    console.print(Panel(
        "[bold magenta]REVIEWER AGENT[/bold magenta]\nReviewing code quality...",
        border_style="magenta"
    ))
    review_result = reviewer.review(state["description"], state["files"])
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
        "file_list": [],
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
        task = progress.add_task("Running pipeline...", total=None)
        result = app.invoke(initial_state)
        progress.update(task, completed=True)

    if save_files and result["files"]:
        project_dir = save_project(result, description[:40])
        console.print(f"\n[bold green]Project saved: {project_dir}[/bold green]")
        console.print("\n[bold]Files:[/bold]")
        for p in sorted(result["files"].keys()):
            console.print(f"  {p}")

    console.print(f"\n[bold green]Done![/bold green] {len(result['files'])} files, {result['iterations']} agent steps")

    return result
