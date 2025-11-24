import importlib.resources as res
from pathlib import Path

from rich.console import Console

console = Console()

def initialize_project():
    base_dir = Path.cwd()
    suites_dir = base_dir / "suites"
    tests_dir = base_dir / "tests"

    suites_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    # Copy template files from package templates
    with res.files("nrobo.templates").joinpath("sample_suite.ymlsss").open("rb") as src:
        (suites_dir / "sample_suite.ymlsss").write_bytes(src.read())

    with res.files("nrobo.templates").joinpath("test_sample.py").open("rb") as src:
        (tests_dir / "test_sample.py").write_bytes(src.read())

    with res.files("nrobo.templates").joinpath("test_sample_another.py").open("rb") as src:
        (tests_dir / "test_sample_another.py").write_bytes(src.read())

    #

    console.print("✨ [bold green]nRoBo project initialized![/]")
    console.print("📂 Created: suites/, tests/")
    console.print("🧩 Added: sample_suite.ymlsss + test_sample.py + test_sample_another.py")
