import subprocess
from unittest.mock import patch

import pytest

from nrobo.core.constants import ExitCodes
from nrobo.core.exceptions import DependencyNotFoundError
from nrobo.helpers.reporting_helper import check_dependency, generate_allure_report


@pytest.mark.parametrize(
    "tool,exists",
    [
        ("git", True),
        ("some-fake-tool", False),
    ],
)
def test_check_dependency(tool, exists):
    with patch("shutil.which") as mocked_which:
        # Simulate presence or absence of the tool
        mocked_which.return_value = "/usr/bin/" + tool if exists else None
        install_hint = f"Install {tool} with apt"
        if exists:
            # Should not raise
            check_dependency(tool)
        else:
            with pytest.raises(DependencyNotFoundError) as exc_info:
                check_dependency(tool, install_hint=install_hint)

            assert exc_info.value.return_code == ExitCodes.DEP_NOT_FOUND
            assert exc_info.value.dependency == tool
            message = f"❌ Required dependency/CLI not found: {tool}"
            message += f"\n   💡 To fix: {install_hint}"
            assert exc_info.value.install_hint == install_hint


def test_generate_allure_report_handles_called_process_error(caplog):
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd="allure generate ...",
        output="some output",
        stderr="some error"
    )

    with (
        patch("nrobo.helpers.reporting_helper.check_dependency"),
        patch("subprocess.run", side_effect=error)
    ):
        generate_allure_report()

    assert "❌ Failed to generate Allure report." in caplog.text
    assert "Command: allure generate ..." in caplog.text
    assert "Exit Code: 1" in caplog.text
    assert "Output: some output" in caplog.text
    assert "Error Output: some error" in caplog.text