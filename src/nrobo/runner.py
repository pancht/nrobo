import pytest
import yaml
from pathlib import Path

def run_tests(suite=None, pytest_args=None):
    test_dir = Path.cwd() / "tests"
    suite_dir = Path.cwd() / "suites"

    selected_tests = [str(test_dir)]
    if suite:
        suite_path = suite_dir / suite
        if suite_path.exists():
            with open(suite_path) as f:
                suite_data = yaml.safe_load(f)
            for t in suite_data.get("tests", []):
                selected_tests.append(str(test_dir / t))

    pytest_options = selected_tests

    if pytest_args:
        # Append all extra pytest args (supports -v, -k test, --maxfail=1, etc.)
        pytest_options.extend(pytest_args)

    return pytest_options
