import pytest
import typer
from pathlib import Path
from .runner import run_tests
from .utils import initialize_project

app = typer.Typer(
    help="nRoBo - Smart Test Runner built on Pytest",
    add_completion=False,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)

@app.command()
def init():
    """Initialize a new nRoBo project with sample suite and tests."""
    initialize_project()

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    suite: str = typer.Option(
        None,
        "--suite",
        help="Suite YAML file name under suites/ (optional; if omitted, all tests will run or first suite will be used).",
    ),
    browser: str = typer.Option(
        "chrome",
        "-b",
        "--browser",
        help="Browser to run tests on (chrome, firefox, edge, etc.)",
    ),
):
    """Default command: run tests if --suite provided, else run all tests."""
    pytest_args = ctx.args

    # auto-detect suite if not provided
    if suite is None:
        suites_dir = Path.cwd() / "suites"
        yml_files = list(suites_dir.glob("*.yml"))
        if yml_files:
            suite = yml_files[0].name
            typer.echo(f"No --suite provided. Auto-detected suite: {suite}")
        else:
            typer.echo("No suite specified and no suite files found. Running all tests...")
            suite = None  # will run all tests in `tests/`

    typer.echo(f"Starting nRoBo test execution on browser: {browser} ...")

    pytest_options = run_tests(suite=suite, pytest_args=pytest_args) #, browser=browser)
    exit_code = pytest.main(pytest_options)
    raise typer.Exit(code=exit_code)

def main():
    app()

if __name__ == "__main__":
    main()
