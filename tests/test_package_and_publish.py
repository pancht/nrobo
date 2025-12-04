import sys
from pathlib import Path
from unittest.mock import patch

import package_and_publish

# Add parent dir so we can import package_and_publish
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_bump_version():
    assert package_and_publish.bump_version("1.2.3", "patch") == "1.2.4"
    assert package_and_publish.bump_version("1.2.3", "minor") == "1.3.0"
    assert package_and_publish.bump_version("1.2.3", "major") == "2.0.0"


@patch("requests.get")
def test_get_latest_pypi_version_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"info": {"version": "2.1.0"}}
    version = package_and_publish.get_latest_pypi_version("nrobo", test=False)
    assert version == "2.1.0"


@patch("requests.get", side_effect=Exception("timeout"))
def test_get_latest_pypi_version_failure(mock_get):
    version = package_and_publish.get_latest_pypi_version("nrobo", test=True)
    assert version == "0.0.0"


@patch("builtins.input", return_value="n")
@patch("package_and_publish.subprocess.run")
@patch("package_and_publish.clear_dist_folder")
@patch("package_and_publish.update_version_file")
@patch("package_and_publish.tomlkit.parse")
def test_main_dry_run_cancel_upload(mock_parse, mock_update, mock_clear, mock_run, mock_input):
    mock_doc = {"project": {"name": "nrobo", "version": "0.1.0"}}
    mock_parse.return_value = mock_doc

    # 👇 patch Path.read_text globally, not on PYPROJECT
    with (
        patch("pathlib.Path.read_text", return_value="dummy-toml"),
        patch("pathlib.Path.write_text") as mock_write,
        patch("package_and_publish.get_latest_pypi_version", return_value="0.0.1"),
        patch("package_and_publish.show_git_changelog"),
        patch("sys.argv", ["script", "--level", "minor", "--dry"]),
    ):
        package_and_publish.main()
        mock_run.assert_not_called()
        mock_write.assert_not_called()


@patch("builtins.input", return_value="y")
@patch("package_and_publish.subprocess.run")
@patch("package_and_publish.clear_dist_folder")
@patch("package_and_publish.update_version_file")
@patch("package_and_publish.tomlkit.parse")
def test_main_real_flow(mock_parse, mock_update, mock_clear, mock_run, mock_input):
    mock_doc = {"project": {"name": "nrobo", "version": "0.1.0"}}
    mock_parse.return_value = mock_doc

    # 👇 again patch Path methods globally
    with (
        patch("pathlib.Path.read_text", return_value="dummy-toml"),
        patch("pathlib.Path.write_text") as mock_write,
        patch("package_and_publish.get_latest_pypi_version", return_value="0.0.1"),
        patch("package_and_publish.show_git_changelog"),
        patch("sys.argv", ["script", "--level", "minor", "--no-git-log"]),
    ):
        package_and_publish.main()
        assert mock_run.call_count >= 2
        mock_write.assert_called_once()
        mock_update.assert_called_once()
