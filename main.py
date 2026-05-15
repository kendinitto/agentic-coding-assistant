import argparse
import sys
from orchestrator import run_pipeline
from rich.console import Console
from rich.panel import Panel

console = Console()

SAMPLE_PROMPTS = [
    "A REST API for task management with user auth and JWT tokens",
    "A Python CLI todo app with SQLite storage",
    "A URL shortener service with click tracking",
    "A web scraper that saves product data to CSV",
    "A disk usage monitor CLI with email alerts",
]


def print_welcome():
    console.print(Panel(
        "[bold]Agentic Coding Assistant[/bold]\n\n"
        "Multi-agent system that turns natural language into production code.\n\n"
        "Agents:\n"
        "  1. [cyan]Planner[/cyan]     - Breaks down requirements\n"
        "  2. [blue]Architect[/blue]  - Designs file structure (JSON)\n"
        "  3. [green]Coder[/green]      - Generates each file individually\n"
        "  4. [magenta]Reviewer[/magenta]  - Reviews code quality\n\n"
        "Output: Complete project directory with source code + review.\n"
        "LLM: local llama.cpp or OpenAI API",
        border_style="white",
        title="Welcome",
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Coding Assistant - Natural language to production code"
    )
    parser.add_argument("prompt", nargs="?", help="Describe the app to build")
    parser.add_argument("--stack", "-s", default="", help="Tech stack (e.g., Python/FastAPI/PostgreSQL)")
    parser.add_argument("--list-prompts", action="store_true", help="List sample prompts")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--no-save", action="store_true", help="Don't save files")

    args = parser.parse_args()

    if args.list_prompts:
        console.print("[bold]Sample Prompts:[/bold]")
        for i, p in enumerate(SAMPLE_PROMPTS, 1):
            console.print(f"  {i}. {p}")
        sys.exit(0)

    prompt = args.prompt
    if args.demo and not prompt:
        prompt = SAMPLE_PROMPTS[1]
        console.print("[bold yellow]Demo mode[/bold yellow]\n")

    if not prompt:
        print_welcome()
        parser.print_help()
        sys.exit(0)

    print_welcome()
    console.print(f"\n[bold]Building: {prompt}[/bold]\n")
    run_pipeline(prompt, args.stack, save_files=not args.no_save)


if __name__ == "__main__":
    main()
