import argparse
import sys
from orchestrator import run_pipeline
from rich.console import Console
from rich.panel import Panel

console = Console()

SAMPLE_PROMPTS = [
    "A REST API for a task management app with user authentication, CRUD operations, and JWT tokens",
    "A web scraper that extracts product data from e-commerce sites and saves to CSV",
    "A real-time chat application with WebSocket support and message history",
    "A URL shortener service with analytics tracking and expiry dates",
    "A CLI tool that monitors disk usage and sends alerts when thresholds are exceeded",
]


def print_welcome():
    console.print(Panel(
        "[bold]Agentic Coding Assistant[/bold]\n\n"
        "Multi-agent system that turns natural language into production code.\n\n"
        "Orchestrates 4 specialized agents:\n"
        "  1. [cyan]Planner[/cyan]     - Breaks down requirements into actionable plan\n"
        "  2. [blue]Architect[/blue]  - Designs system architecture and file structure\n"
        "  3. [green]Coder[/green]      - Generates complete, production-quality code\n"
        "  4. [magenta]Reviewer[/magenta]  - Reviews code quality, generates README\n\n"
        "Output: Complete project with code, README, and code review report.\n"
        "LLM: local llama.cpp or OpenAI API",
        border_style="white",
        title="Welcome",
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Coding Assistant - Natural language to production code"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Describe the application you want to build",
    )
    parser.add_argument(
        "--stack", "-s",
        default="",
        help="Preferred tech stack (e.g., 'Python/FastAPI/PostgreSQL')",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List sample prompts",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with a sample prompt",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save generated files to disk",
    )

    args = parser.parse_args()

    if args.list_prompts:
        console.print("[bold]Sample Prompts:[/bold]")
        for i, prompt in enumerate(SAMPLE_PROMPTS, 1):
            console.print(f"  {i}. {prompt}")
        sys.exit(0)

    prompt = args.prompt

    if args.demo and not prompt:
        prompt = SAMPLE_PROMPTS[0]
        console.print("[bold yellow]Running demo mode...[/bold yellow]\n")

    if not prompt:
        print_welcome()
        parser.print_help()
        console.print("\n[bold]Usage examples:[/bold]")
        console.print('  python main.py "REST API for task management"')
        console.print('  python main.py "URL shortener" --stack Python/FastAPI/Redis')
        console.print("  python main.py --demo")
        console.print("  python main.py --list-prompts")
        sys.exit(0)

    print_welcome()
    console.print(f"\n[bold]Building: {prompt}[/bold]\n")

    result = run_pipeline(prompt, args.stack, save_files=not args.no_save)

    console.print("\n" + "=" * 60)
    console.print("[bold]Output Summary[/bold]")
    console.print(f"  Plan:       {len(result['plan'])} chars")
    console.print(f"  Architecture: {len(result['architecture'])} chars")
    console.print(f"  Code:       {len(result['raw_code'])} chars")
    console.print(f"  Files:      {len(result['files'])}")
    console.print(f"  Review:     {len(result['review'])} chars")
    console.print(f"  Review:     {len(result['review'])} chars")
    console.print("=" * 60)


if __name__ == "__main__":
    main()
