from nrobo.generators.page_generator import generate_page_file, to_snake


def test_to_snake_converts_camel_to_snake():
    assert to_snake("LoginPage") == "login_page"
    assert to_snake("Home") == "home"
    assert to_snake("MySuperPage") == "my_super_page"


def test_generate_page_file_creates_files(tmp_path, monkeypatch, capsys):
    # Arrange
    pages_dir = tmp_path / "pages"
    monkeypatch.chdir(tmp_path)

    # Act
    generate_page_file("LoginPage")

    # Assert
    page_file = pages_dir / "login_page.py"
    locator_file = pages_dir / "login_page_locators.py"

    assert page_file.exists(), "Page file should be created"
    assert locator_file.exists(), "Locator file should be created"

    content = page_file.read_text()
    loc_content = locator_file.read_text()
    assert "class LoginPage(BasePage)" in content
    assert "class LoginPageLocators" in loc_content

    out = capsys.readouterr().out
    assert "✔ Created page:" in out
    assert "✔ Created locator file:" in out


def test_generate_page_file_when_files_exist(tmp_path, monkeypatch, capsys):
    # Arrange
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    page_file = pages_dir / "login_page.py"
    locator_file = pages_dir / "login_page_locators.py"

    # Pre-create files to trigger 'already exists' branch
    page_file.write_text("dummy")
    locator_file.write_text("dummy")

    monkeypatch.chdir(tmp_path)

    # Act
    generate_page_file("LoginPage")

    # Assert
    out = capsys.readouterr().out
    assert "⚠ Page already exists:" in out
    assert "⚠ Locator file already exists:" in out
    # Ensure no overwrite occurred
    assert page_file.read_text() == "dummy"
    assert locator_file.read_text() == "dummy"
