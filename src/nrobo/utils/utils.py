import importlib.resources as res
from pathlib import Path

from rich.console import Console

console = Console()

def initialize_project():
    base_dir = Path.cwd()
    suites_dir = base_dir / "suites"
    tests_dir = base_dir / "tests"
    ui_dir = tests_dir / "ui"
    api_dir = tests_dir / "api"
    mobile_dir = tests_dir / "mobile"
    reports_dir = base_dir / "reports"
    allure_reports_dir = base_dir / "allure-reports"
    allure_results_dir = base_dir / "allure-results"

    suites_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)
    ui_dir.mkdir(exist_ok=True)
    api_dir.mkdir(exist_ok=True)
    mobile_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)
    allure_reports_dir.mkdir(exist_ok=True)
    allure_results_dir.mkdir(exist_ok=True)

    # Copy template files from package templates
    with res.files("nrobo.templates").joinpath("sample_suite.yml").open("rb") as src:
        (suites_dir / "sample_suite.yml").write_bytes(src.read())

    with res.files("nrobo.templates").joinpath("test_sample.py").open("rb") as src:
        (ui_dir / "test_sample.py").write_bytes(src.read())

    with res.files("nrobo.templates").joinpath("test_sample_another.py").open("rb") as src:
        (ui_dir / "test_sample_another.py").write_bytes(src.read())

    #

    console.print("✨ [bold green]nRoBo project initialized![/]")
    console.print("📂 Created: suites/, tests/")
    console.print("🧩 Added: sample_suite.yml + test_sample.py + test_sample_another.py")
