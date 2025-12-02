import pytest

from nrobo.cli.commands.init import load_and_inject_template, init_project

# Sample minimal template for testing
TEMPLATE_YAML = """
project:
  name: "{{project_name}}"

folders:
  - foo/bar
  - baz

files:
  hello.txt: "Hello {{project_name}}!"
  foo/info.txt: "Project: {{project_name}}"
"""


@pytest.fixture
def fake_template_path(tmp_path):
    path = tmp_path / "template.yaml"
    path.write_text(TEMPLATE_YAML)
    return path


def test_template_injection(fake_template_path):
    result = load_and_inject_template(fake_template_path, "MyCoolApp")
    assert result["project"]["name"] == "MyCoolApp"
    assert "folders" in result
    assert "files" in result
    assert "hello.txt" in result["files"]
    assert "MyCoolApp" in result["files"]["hello.txt"]


def test_init_project_creates_dirs_and_files(tmp_path, fake_template_path, mocker):
    mock_initialize = mocker.patch("nrobo.cli.commands.init.initialize_project")

    init_project(fake_template_path, "TestApp", base_path=tmp_path)

    # Verify folders created
    assert (tmp_path / "foo" / "bar").is_dir()
    assert (tmp_path / "baz").is_dir()

    # Verify files created and contain rendered content
    hello_path = tmp_path / "hello.txt"
    assert hello_path.is_file()
    assert "TestApp" in hello_path.read_text()

    info_path = tmp_path / "foo" / "info.txt"
    assert info_path.is_file()
    assert "Project: TestApp" in info_path.read_text()

    # Ensure initialize_project() was called
    mock_initialize.assert_called_once()
