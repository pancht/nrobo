from pathlib import Path
from unittest.mock import patch

from nrobo.utils.tests_discovery_utils import has_pytest_tests


def test_has_pytest_tests_finds_test_file(tmp_path: Path, caplog):
    # Arrange
    test_file = tmp_path / "test_example.py"
    test_file.write_text("def test_dummy(): pass")

    # Act
    with caplog.at_level("DEBUG"):
        result = has_pytest_tests(str(tmp_path))

    # Assert
    assert result is True
    assert "✅ Found test file" in caplog.text


def test_has_pytest_tests_returns_false_if_no_tests(tmp_path: Path):
    # Arrange: Create non-test file
    non_test_file = tmp_path / "example.py"
    non_test_file.write_text("# not a test")

    # Act
    result = has_pytest_tests(str(tmp_path))

    # Assert
    assert result is False


def test_has_pytest_tests_with_nested_test_file(tmp_path: Path):
    nested_dir = tmp_path / "subdir"
    nested_dir.mkdir()
    (nested_dir / "test_nested.py").write_text("def test_nested(): pass")

    assert has_pytest_tests(str(tmp_path)) is True


def test_has_pytest_tests_with_default_dir_not_found():
    # No "tests/" folder in current dir
    with patch("os.walk", return_value=[]):
        assert has_pytest_tests("nonexistent") is False
