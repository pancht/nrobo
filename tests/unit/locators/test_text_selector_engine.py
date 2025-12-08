from unittest.mock import MagicMock

from nrobo.locators.text_selector_engine import TextSelectorEngine


def test_find_by_text_executes_correct_js_and_returns_result():
    driver = MagicMock()
    driver.execute_script.return_value = ["el1", "el2"]

    result = TextSelectorEngine.find_by_text(driver, "Login")

    assert result == ["el1", "el2"]

    # Check correct JS is passed
    driver.execute_script.assert_called_once()
    script, text_arg = driver.execute_script.call_args[0]

    assert "document.createTreeWalker" in script
    assert "t.includes(text)" in script
    assert text_arg == "Login"


def test_regex_match_executes_correct_js_and_returns_result():
    driver = MagicMock()
    driver.execute_script.return_value = ["match1"]

    result = TextSelectorEngine.regex_match(driver, r"Logi.*")

    assert result == ["match1"]

    script, pattern_arg = driver.execute_script.call_args[0]

    assert "new RegExp(arguments[0], 'i')" in script
    assert pattern_arg == r"Logi.*"


def test_find_has_text_executes_correct_js_and_returns_result():
    driver = MagicMock()
    driver.execute_script.return_value = ["btn1", "btn2"]

    result = TextSelectorEngine.find_has_text(driver, "button", "Save")

    assert result == ["btn1", "btn2"]

    script, selector_arg, text_arg = driver.execute_script.call_args[0]

    assert "document.querySelectorAll" in script
    assert "t.includes(text)" in script
    assert selector_arg == "button"
    assert text_arg == "Save"
