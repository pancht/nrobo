import textwrap

import pytest


def test_cli_triggers_playwright_lifecycle_and_cleanup(mocker, tmp_path):
    """
    Integration test that:
    - Triggers nRoBo CLI via patch
    - Runs a real Playwright test
    - Forces _cleanup_driver execution
    - Covers Playwright teardown lines
    """

    # -------------------------------------------------
    # 1. Create INNER pytest test dynamically
    # -------------------------------------------------
    test_file = tmp_path / "test_inner_playwright_cleanup.py"

    test_file.write_text(
        textwrap.dedent(
            """
            import pytest
            from playwright.sync_api import Page

            @pytest.mark.playwright
            def test_inner_cleanup(page: Page):
                # Minimal action to ensure fixture is used
                page.goto("about:blank")
            """
        )
    )

    # -------------------------------------------------
    # 2. Spy on _cleanup_driver (THIS is the key fix)
    # -------------------------------------------------
    from nrobo.plugins.nrobo_plugin import nRoboWebDriverPlugin

    real_cleanup = nRoboWebDriverPlugin._cleanup_driver  # noqa: F841
    cleanup_spy = mocker.spy(nRoboWebDriverPlugin, "_cleanup_driver")

    # -------------------------------------------------
    # 3. Patch pytest.main (wrap, don't mock)
    # -------------------------------------------------
    real_pytest_main = pytest.main

    def wrapped_pytest_main(args):
        return real_pytest_main(args)

    spy = mocker.patch("pytest.main", side_effect=wrapped_pytest_main)

    # -------------------------------------------------
    # 4. Invoke nRoBo CLI entry
    # -------------------------------------------------
    from nrobo.cli.main import run_pytest_safely

    exit_code = run_pytest_safely(
        [
            str(test_file),
            "--engine=playwright",
            "--basetemp",
            str(tmp_path / ".pytest_tmp"),
        ]
    )

    # -------------------------------------------------
    # 5. Assertions
    # -------------------------------------------------
    spy.assert_called_once()
    cleanup_spy.assert_called()  # teardown executed

    called_args = spy.call_args[1]["args"]
    assert "--engine=playwright" in called_args
    assert exit_code == 0
