from pathlib import Path
from unittest.mock import patch

import pytest

from nrobo.core import settings
from nrobo.core.exceptions import SuiteNotFoundError
from nrobo.helpers.validations import validate_suite_paths  # Adjust path as needed


def test_validate_suite_paths_all_exist(tmp_path: Path):
    # Arrange
    suite_names = ["smoke.yml", "regression.yml"]
    for name in suite_names:
        (tmp_path / name).write_text("robot_suite: true")

    with patch.object(settings, "SUITES_DIR", tmp_path):
        # Act & Assert: Should NOT raise
        validate_suite_paths(suite_names)


def test_validate_suite_paths_missing_file(tmp_path: Path):
    # Arrange
    suite_names = ["missing.yml"]

    with patch.object(settings, "SUITES_DIR", tmp_path):
        # Act & Assert: Should raise for missing file
        with pytest.raises(SuiteNotFoundError) as exc_info:
            validate_suite_paths(suite_names)

        assert "missing.yml" in str(exc_info.value)


def test_validate_suite_paths_with_none_or_empty(tmp_path: Path):
    with patch.object(settings, "SUITES_DIR", tmp_path):
        # Act & Assert: Should NOT raise on None or empty list
        assert validate_suite_paths(None) is None
        assert validate_suite_paths([]) is None
