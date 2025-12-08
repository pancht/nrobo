import pytest

from nrobo.locators.locator_classifier import LocatorClassifier, LocatorType


@pytest.mark.parametrize(
    "locator, expected",
    [
        # Playwright locators
        ("text=Login", LocatorType.PLAYWRIGHT),
        ("role=button[name='submit']", LocatorType.PLAYWRIGHT),
        ("label=Username", LocatorType.PLAYWRIGHT),
        # XPath locators
        ("//div[@id='header']", LocatorType.XPATH),
        (".//span", LocatorType.XPATH),
        ("/html/body/div", LocatorType.XPATH),
        ("..", LocatorType.XPATH),
        ("//a[contains(text(),'Home')]", LocatorType.XPATH),
        ("//div[@class='x']", LocatorType.XPATH),  # Contains '(@'
        # CSS selectors
        ("div.class", LocatorType.CSS),
        ("#elementId", LocatorType.CSS),
        ("div > span", LocatorType.CSS),
        ("input[type='text']", LocatorType.CSS),
        ("a:hover", LocatorType.CSS),
        # Simple ID / NAME
        ("loginForm", LocatorType.ID),
        ("user_123", LocatorType.ID),
        ("NAME_001", LocatorType.ID),
        # Unknown (won't match any rule)
        ("123 @invalid", LocatorType.UNKNOWN),
        ("", LocatorType.UNKNOWN),
        ("    ", LocatorType.UNKNOWN),
    ],
)
def test_locator_detection(locator, expected):
    assert LocatorClassifier.detect(locator) == expected
