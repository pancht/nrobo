import pytest

from nrobo.locators.has_text_selector_parser import HasTextEngine, HasTextParser

# ------------------------------
# Tests for HasTextParser
# ------------------------------


def test_parse_valid_double_quotes():
    """Should correctly parse selector with double quotes."""
    selector = 'h3:has-text("Welcome")'
    base, text = HasTextParser.parse(selector)

    assert base == "h3"
    assert text == "Welcome"


def test_parse_valid_single_quotes():
    """Should correctly parse selector with single quotes."""
    selector = "div:has-text('Submit')"
    base, text = HasTextParser.parse(selector)

    assert base == "div"
    assert text == "Submit"


def test_parse_with_spaces_and_trimming():
    """Should strip spaces around base selector and text."""
    selector = 'span :has-text("Click Me")'
    base, text = HasTextParser.parse(selector)

    assert base == "span"
    assert text == "Click Me"


@pytest.mark.parametrize(
    "invalid_selector",
    [
        "div",  # Missing :has-text
        "div:has-text()",  # Empty parentheses
        "div:has-text('abc') extra",  # Extra text
        "has-text('abc')",  # Missing base selector
        "div:has-txt('abc')",  # Typo in pseudo-class
    ],
)
def test_parse_invalid_selectors_raise_error(invalid_selector):
    """Should raise ValueError for invalid selectors."""
    with pytest.raises(ValueError, match="Invalid :has-text selector"):
        HasTextParser.parse(invalid_selector)


# ------------------------------
# Tests for HasTextEngine
# ------------------------------


def test_to_xpath_generates_correct_expression():
    """Should generate a valid XPath expression for given base and text."""
    result = HasTextEngine.to_xpath("h3", "Welcome")
    expected = './/h3[contains(normalize-space(.), "Welcome")]'
    assert result == expected


def test_to_xpath_handles_special_chars():
    """Should still work even if text contains spaces or punctuation."""
    result = HasTextEngine.to_xpath("p", "Hello, world!")
    assert result == './/p[contains(normalize-space(.), "Hello, world!")]'
