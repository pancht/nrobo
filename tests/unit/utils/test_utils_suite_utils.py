from pathlib import Path
from unittest.mock import patch

import pytest

from nrobo.core import settings
from nrobo.core.exceptions import NoTestsFoundException
from nrobo.utils.suite_utils import detect_or_validate_suites


def test_detect_or_validate_suites_autodetect_with_yml(tmp_path: Path, caplog):
    # Create dummy YML suite
    fake_suite_dir = tmp_path / "suites"
    fake_suite_dir.mkdir(parents=True, exist_ok=True)
    fake_suite = fake_suite_dir / "sample_suite.yml"
    fake_suite.write_text("robot_suite: true")

    with (
        patch.object(settings, "SUITES_DIR", fake_suite_dir),
        patch("nrobo.utils.suite_utils.has_pytest_tests", return_value=True),
        caplog.at_level("INFO"),
    ):

        result = detect_or_validate_suites()

        assert result == []
        assert "Auto-detected 1 suite file" in caplog.text


def test_detect_or_validate_suites_no_suites_and_no_tests(tmp_path: Path):
    fake_suite_dir = tmp_path / "suites"
    fake_suite_dir.mkdir(parents=True, exist_ok=True)

    with (
        patch.object(settings, "SUITES_DIR", fake_suite_dir),
        patch("nrobo.utils.suite_utils.has_pytest_tests", return_value=False),
    ):

        with pytest.raises(NoTestsFoundException):
            detect_or_validate_suites()


def test_detect_or_validate_suites_validates_explicit_suites():
    test_suites = ["suite1.yml", "suite2.yml"]

    with (
        patch("nrobo.utils.suite_utils.validate_suite_paths") as mock_validate,
        patch(
            "nrobo.utils.suite_utils.deduplicate_preserve_order", side_effect=lambda s: s
        ) as mock_dedup,
    ):

        result = detect_or_validate_suites(test_suites)

        mock_validate.assert_called_once_with(suites=test_suites)
        mock_dedup.assert_called_once_with(test_suites)
        assert result == test_suites
