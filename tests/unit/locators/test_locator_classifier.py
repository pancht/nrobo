import pytest

from nrobo.locators.locator_classifier import LocatorClassifier, LocatorType


@pytest.mark.parametrize("loc", ["role=button", "label=Username"])
def test_detect_playwright(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.PLAYWRIGHT


@pytest.mark.parametrize(
    "loc",
    [
        "//div",
        "/html/body/div",
        ".//span[@id='x']",
        "..//button",
        "//a[@href]",
        "//*[@id='x']",
        "div(@something)",  # contains "(@"
    ],
)
def test_detect_xpath(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.XPATH


@pytest.mark.parametrize(
    "loc",
    [
        ".class",
        "#id",
        "div > span",
        "button[disabled]",
        "input[type='text']",
        "ul li.item",
        "form[name=login]",
    ],
)
def test_detect_css(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.CSS


@pytest.mark.parametrize("loc", ["shadow::#root >>> button", "#a >>> #b", "div >>> span"])
def test_detect_shadow(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.SHADOW


@pytest.mark.parametrize("loc", ["text=Login", "text=Submit Now"])
def test_detect_text_explicit(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.PLAYWRIGHT


@pytest.mark.parametrize(
    "loc",
    [
        '"Login"',
        "'Submit'",
    ],
)
def test_detect_text_quoted(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.TEXT


def test_detect_has_text():
    loc = "div:has-text('Login')"
    assert LocatorClassifier.detect(loc) == LocatorType.HAS_TEXT


def test_detect_has():
    loc = "section:has(div.item)"
    assert LocatorClassifier.detect(loc) == LocatorType.HAS


@pytest.mark.parametrize(
    "loc",
    [
        "button:visible",
        "input:hidden",
        "div:enabled",
        "a:disabled",
        "span:checked",
        "button:not(.hidden)",
    ],
)
def test_detect_pseudo(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.PSEUDO


@pytest.mark.parametrize("loc", ["username", "inputField", "btn_login", "header123"])
def test_detect_id_guess(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.ID


@pytest.mark.parametrize(
    "loc",
    [
        "   ",  # empty/whitespace
        "@@@",  # nonsensical
        "🚀invalid",  # unicode emoji
        "???",  # unknown pattern
    ],
)
def test_detect_unknown(loc):
    assert LocatorClassifier.detect(loc) == LocatorType.UNKNOWN


def test_detect_text_explicit_():
    assert LocatorClassifier.detect("text=Login") == LocatorType.PLAYWRIGHT
    assert LocatorClassifier.detect("text=Submit Now") == LocatorType.PLAYWRIGHT
    assert LocatorClassifier.detect("text=Hello123") == LocatorType.PLAYWRIGHT


@pytest.mark.parametrize(
    "locator", ["text=Hello", "role=button", "label=Username", "link=Home", "partial-text=Welcome"]
)
def test_detect_returns_playwright_for_supported_prefixes(locator):
    """
    Ensure detect() returns LocatorType.PLAYWRIGHT when locator has '=' and prefix
    in {'text', 'role', 'label', 'link', 'partial-text'}.
    """
    result = LocatorClassifier.detect(locator)
    assert result == LocatorType.PLAYWRIGHT
