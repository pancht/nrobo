import os

import yaml
from pathlib import Path
from typing import List, Optional, Union

def prepare_pytest_cli_options(
    suites: Optional[Union[str, List[str]]] = None,
    pytest_args: Optional[List[str]] = None
) -> List[str]:
    """
    Build the final list of pytest CLI options based on suite YAML files and extra args.

    Args:
        suites: Single suite file name, list of suite files, or None.
        pytest_args: Additional pytest command-line arguments.

    Returns:
        List of pytest CLI arguments to pass to pytest.main().
    """
    test_dir = Path.cwd() / "tests"
    suite_dir = Path.cwd() / "suites"

    # Start with default: run all tests if no suite provided
    selected_tests = [str(test_dir)]

    if suites:
        selected_tests = []  # override default
        suite_files = [suites] if isinstance(suites, str) else suites

        for suite_file in suite_files:
            suite_path = suite_dir / suite_file
            if not suite_path.exists():
                print(f"⚠️ Suite file not found: {suite_file}")
                continue

            try:
                with open(suite_path, "r", encoding="utf-8") as f:
                    suite_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ Failed to read suite '{suite_file}': {e}")
                continue

            for t in suite_data.get("tests", []):
                test_path = test_dir / t
                selected_tests.append(str(test_path))

    # Merge pytest args
    pytest_options = selected_tests + (pytest_args or [])

    return pytest_options


def run_with_allure():
    results_dir = os.path.join(os.getcwd(), "allure-results")
    report_dir = os.path.join(os.getcwd(), "allure-report")

    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    # 1️⃣ Run tests and collect allure results
    pytest_args = ["-v", "--alluredir", results_dir]
    pytest.main(pytest_args)

    # 2️⃣ Generate allure report (HTML)
    subprocess.run(["allure", "generate", results_dir, "-o", report_dir, "--clean"], check=True)

    print(f"✅ Allure report ready: file://{os.path.abspath(report_dir)}/index.html")
