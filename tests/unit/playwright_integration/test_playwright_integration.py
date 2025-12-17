import pytest


def test_cli_triggers_playwright_lifecycle(mocker, tmp_path):
    """
    Integration test:
    - Triggers nRoBo CLI via patch
    - Executes pytest with --engine=playwright
    - Ensures pytest.main is called correctly
    """

    # ---------------- Patch pytest.main ----------------
    real_pytest_main = pytest.main

    def wrapped_pytest_main(args):
        # Delegate to real pytest.main so tests actually run
        return real_pytest_main(args)

    spy = mocker.patch("pytest.main", side_effect=wrapped_pytest_main)

    # ---------------- Call CLI entry ----------------
    from nrobo.cli.main import run_pytest_safely

    exit_code = run_pytest_safely(
        [
            "--engine=playwright",
            "-k",
            "test_navigation_actions",
            "--basetemp",
            str(tmp_path),
        ]
    )

    # ---------------- Assertions ----------------
    spy.assert_called_once()

    called_args = spy.call_args[1]["args"]

    assert "--engine=playwright" in called_args
    assert exit_code == 0
