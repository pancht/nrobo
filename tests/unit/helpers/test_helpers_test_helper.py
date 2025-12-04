from nrobo.helpers.test_helper import (
    _create_a_failing_test,
    _create_a_failing_ui_test,
    _create_a_passing_test,
    _create_coveragerc_tmp_file,
)


def test_create_a_passing_test_creates_file_with_test(tmp_path):
    # Create a temporary directory for the test
    test_dir = tmp_path / "unit_tests"

    # Call the function
    test_file = _create_a_passing_test(test_dir)

    # Assertions
    assert test_file.exists()
    assert test_file.name.startswith("test_passing_unit_test_")
    assert test_file.suffix == ".py"

    content = test_file.read_text()
    assert "def test_addition()" in content
    assert "assert 1 + 1 == 2" in content


def test_create_a_failing_test_creates_file_with_failing_test(tmp_path):
    # Create a temporary test directory
    test_dir = tmp_path / "fail_tests"

    # Create the failing test file
    test_file = _create_a_failing_test(test_dir)

    # ✅ Check file was created with correct naming and extension
    assert test_file.exists()
    assert test_file.name.startswith("test_failing_unit_test_")
    assert test_file.suffix == ".py"

    # ✅ Check test content
    content = test_file.read_text()
    assert "def test_addition()" in content
    assert "assert 1 + 1 == 3" in content


def test_create_a_failing_ui_test_creates_test_file(tmp_path):
    test_dir = tmp_path / "ui_tests"

    test_file = _create_a_failing_ui_test(test_dir)

    # ✅ Verify file creation
    assert test_file.exists()
    assert test_file.name.startswith("test_failing_ui_test_")
    assert test_file.suffix == ".py"

    # ✅ Check content
    content = test_file.read_text()
    assert "def test_google_home_loading_failing_test" in content
    assert "from nrobo.selenium_wrappers.nrobo_selenium_wrapper import" in content
    assert "from nrobo.templates.home_page import PageHome" in content
    assert "google_home_page.get(url)" in content
    assert "assert not google_home_page.is_page_visible()" in content


def test_create_coveragerc_tmp_file(tmp_path):
    # Act
    coveragerc_path = _create_coveragerc_tmp_file(tmp_path)

    # ✅ Check file path
    assert coveragerc_path.exists()
    assert coveragerc_path.name == ".coveragerc"
    assert "configs" in str(coveragerc_path)

    # ✅ Check content
    content = coveragerc_path.read_text()

    assert "[run]" in content
    assert "source = " + str(tmp_path) in content
    assert "disable_warnings = no-data-collected" in content
    assert "omit =" in content
    assert "[report]" in content
    assert "show_missing = True" in content
