import typer
import pytest
from .runner import run_tests

app = typer.Typer(help="nRoBo - Smart Test Runner built on Pytest")

@app.command()
def run(
    suite: str = typer.Option(None, "--suite", "-s", help="Suite YAML file name under suites/"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    **pytest_args
):
    """Run tests via nrobo."""
    typer.echo("Starting nRoBo test execution...")
    exit_code = run_tests(suite=suite, verbose=verbose, pytest_args=pytest_args)
    raise typer.Exit(code=exit_code)

def main():
    app()

if __name__ == "__main__":
    main()
