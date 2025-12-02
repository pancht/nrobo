import pytest

from nrobo.utils.update_version_utils import update_version_file


def test_update_version_file_success(tmp_path, capsys):
    version_file = tmp_path / "version.py"
    original_content = '__version__ = "0.1.0"\n'
    version_file.write_text(original_content)

    update_version_file(str(version_file), "1.2.3")

    updated = version_file.read_text()
    assert '__version__ = "1.2.3"' in updated

    output = capsys.readouterr().out
    assert f"✅ Version updated to 1.2.3 in {version_file}" in output


def test_update_version_file_missing_file(tmp_path):
    missing_file = tmp_path / "nonexistent.py"

    with pytest.raises(FileNotFoundError) as excinfo:
        update_version_file(str(missing_file), "0.2.0")

    assert "File not found" in str(excinfo.value)


def test_update_version_file_no_version_assignment(tmp_path):
    broken_file = tmp_path / "version.py"
    broken_file.write_text('name = "nrobo"\n')  # No __version__ line

    with pytest.raises(ValueError) as excinfo:
        update_version_file(str(broken_file), "9.9.9")

    assert "Could not find a __version__ assignment" in str(excinfo.value)
