import pytest
import typer

from .runner import run_tests
from .utils import initialize_project

app = typer.Typer(help="nRoBo - Smart Test Runner built on Pytest",
                  add_completion=False,
                  context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
                  )

@app.command()
def init():
    """Initialize a new nRoBo project with sample suite and tests."""
    initialize_project()


@app.command()
def run(ctx: typer.Context,
        suite: str = typer.Option(None, "--suite", help="Suite YAML file name under suites/"),
):
    """Run tests via nrobo."""
    pytest_args = ctx.args
    typer.echo("Starting nRoBo test execution...")
    pytest_options = run_tests(suite=suite, pytest_args=pytest_args)
    exit_code = pytest.main(pytest_options)
    raise typer.Exit(code=exit_code)


def main():
    app()


if __name__ == "__main__":
    main()
