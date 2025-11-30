import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from nrobo.core import settings
from nrobo.utils.command_utils import initialize_project


@patch("importlib.resources.files")
def test_initialize_project_creates_structure_and_copies_templates(
    mock_files, tmp_path: Path, caplog
):
    """✅ initialize_project should create folders and copy templates"""

    # Create mock template files
    fake_template_content = b"mocked content"
    mock_sample_suite = MagicMock()
    mock_sample_suite.open.return_value = io.BytesIO(fake_template_content)

    mock_test_sample = MagicMock()
    mock_test_sample.open.return_value = io.BytesIO(fake_template_content)

    mock_test_sample_another = MagicMock()
    mock_test_sample_another.open.return_value = io.BytesIO(fake_template_content)

    mock_template_dir = MagicMock()
    mock_template_dir.joinpath.side_effect = lambda name: {
        "sample_suite.yml": mock_sample_suite,
        "test_sample.py": mock_test_sample,
        "test_sample_another.py": mock_test_sample_another,
    }[name]

    mock_files.return_value = mock_template_dir

    # Patch settings to redirect paths to tmp_path
    with (
        patch.object(settings, "SUITES_DIR", "suites"),
        patch.object(settings, "TESTS_DIR", "tests"),
        patch.object(settings, "UI_DIR", "ui"),
        patch.object(settings, "API_DIR", "api"),
        patch.object(settings, "MOBILE_DIR", "mobile"),
        patch.object(settings, "HTML_REPORT_PATH", "reports"),
        patch.object(settings, "ALLURE_REPORT_DIR", "allure-reports"),
        patch.object(settings, "ALLURE_RESULTS_DIR", "allure-results"),
        patch.object(settings, "LOG_DIR", "logs"),
        patch.object(settings, "PAGE_OBJECT_DIR", "pages"),
        patch.object(settings, "TEST_DATA_DIR", "test-data"),
        patch("pathlib.Path.cwd", return_value=tmp_path),
        caplog.at_level("INFO"),
    ):

        initialize_project()

        # Assert directory creation
        expected_dirs = [
            "suites",
            "tests",
            "tests/ui",
            "tests/api",
            "tests/mobile",
            "reports",
            "allure-reports",
            "allure-results",
            "logs",
            "pages",
            "test-data",
        ]
        for d in expected_dirs:
            assert (tmp_path / d).exists()

        # Assert files created with correct content
        assert (tmp_path / "suites/sample_suite.yml").read_bytes() == fake_template_content
        assert (tmp_path / "tests/ui/test_sample.py").read_bytes() == fake_template_content
        assert (tmp_path / "tests/ui/test_sample_another.py").read_bytes() == fake_template_content

        # Assert logs
        assert f"{settings.NROBO_APP} project initialized!" in caplog.text
        assert "📂 Created: suites/, tests/" in caplog.text
        assert "🧩 Added: sample_suite.yml + test_sample.py + test_sample_another.py" in caplog.text
