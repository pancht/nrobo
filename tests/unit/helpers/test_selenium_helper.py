from unittest.mock import MagicMock, patch

from selenium.common import JavascriptException

from nrobo.helpers.selenium_helper import (
    _safe_ready_state,
    update_selenium_dependencies,
)


def test_update_selenium_dependencies(capsys):
    with patch("subprocess.run") as mock_run:
        update_selenium_dependencies()

        # Assert subprocess.run was called correctly
        mock_run.assert_called_once_with(
            ["pip", "install", "-U", "selenium", "webdriver-manager"], check=True
        )

        # Assert printed output
        captured = capsys.readouterr()
        assert "Updated Selenium and webdriver-manager" in captured.out


def test_safe_ready_state_returns_document_state():
    """Should return the readyState value when driver executes successfully."""
    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = "complete"

    result = _safe_ready_state(mock_driver)

    assert result == "complete"
    mock_driver.execute_script.assert_called_once_with("return document.readyState")


def test_safe_ready_state_handles_javascript_exception():
    """Should return None when a JavascriptException is raised."""
    mock_driver = MagicMock()
    mock_driver.execute_script.side_effect = JavascriptException("Script error")

    result = _safe_ready_state(mock_driver)

    assert result is None


def test_safe_ready_state_handles_generic_exception():
    """Should return None when any other exception occurs."""
    mock_driver = MagicMock()
    mock_driver.execute_script.side_effect = RuntimeError("Unknown failure")

    result = _safe_ready_state(mock_driver)

    assert result is None
