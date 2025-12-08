from unittest.mock import patch

from nrobo.helpers.selenium_helper import update_selenium_dependencies


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
