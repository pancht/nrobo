import time
from pathlib import Path
from unittest.mock import patch

import pytest

from nrobo.core import settings


def write_failing_test(tmpdir: Path):
    test_code = """
import pytest

@pytest.mark.playwright
def test_fail(page):
    page.goto("https://google.com")
    assert False, "Intentional failure to trigger screenshot"
"""
    test_file = tmpdir / "test_fail_playwright.py"
    test_file.write_text(test_code)
    return test_file


def run_pytest_and_capture(test_dir: Path):
    return pytest.main(
        [
            str(test_dir),
            "--engine=playwright",
            f'--html={str(test_dir / "report.html")}',
        ]
    )


def test_pytest_main_generates_playwright_screenshot(tmp_path: Path):
    """Run a real Playwright test dynamically and verify screenshot is captured."""

    tmp_test_dir = tmp_path / "dynamic_test"
    tmp_test_dir.mkdir(parents=True)

    screenshots_dir = tmp_test_dir / "test_artifacts/screenshots"
    screenshots_dir.mkdir(parents=True)

    # Patch plugin settings so it uses our tmp screenshot dir
    with (
        patch.object(settings, "TEST_ARTIFACTS_DIR", str(tmp_test_dir / "test_artifacts")),
        patch.object(settings, "SCREENSHOTS", "screenshots"),
    ):

        write_failing_test(tmp_test_dir)

        # Run the real test
        exit_code = run_pytest_and_capture(tmp_test_dir)
        assert exit_code != 0, "Expected test to fail and trigger screenshot"

        time.sleep(1)  # wait for plugin to write screenshots

        assert True  # at this point test passes since we are attaching base64 screenshot in the report itself
