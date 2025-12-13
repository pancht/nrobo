import pytest

from nrobo.locators.locator_classifier import LocatorClassifier, LocatorType


@pytest.mark.parametrize(
    "locator, expected",
    [
        # -------------------------
        # PLAYWRIGHT typed selectors
        # -------------------------
        ("text=Login", LocatorType.PLAYWRIGHT),
        ("role=button[name='submit']", LocatorType.PLAYWRIGHT),
        ("label=Username", LocatorType.PLAYWRIGHT),
        ("link=Home", LocatorType.PLAYWRIGHT),
        ("partial-text=Next", LocatorType.PLAYWRIGHT),
        # -------------------------
        # EXPLICIT TEXT (still PLAYWRIGHT)
        # but you ALSO support TEXT type separately
        # Tests will ensure both branches are hit
        ("text=Login", LocatorType.PLAYWRIGHT),
        # -------------------------
        # QUOTED TEXT
        # -------------------------
        ("'Login now'", LocatorType.TEXT),
        ('"Submit"', LocatorType.TEXT),
        # -------------------------
        # XPATH
        # -------------------------
        ("//div[@id='header']", LocatorType.XPATH),
        ("//*[contains(@class, 'active')]", LocatorType.XPATH),
        (".//span", LocatorType.XPATH),
        ("/html/body", LocatorType.XPATH),
        ("..", LocatorType.XPATH),
        ("(//div)[1]", LocatorType.XPATH),
        # -------------------------
        # SHADOW
        # -------------------------
        ("#root >>> button", LocatorType.SHADOW),
        ("shadow::div >>> span", LocatorType.SHADOW),
        ("div >> span", LocatorType.SHADOW),  # PW shadow style
        ("host >> text=Login", LocatorType.SHADOW),
        # -------------------------
        # HAS_TEXT
        # -------------------------
        ("div:has-text('Hello')", LocatorType.HAS_TEXT),
        # -------------------------
        # HAS
        # -------------------------
        ("section:has(div.item)", LocatorType.HAS),
        # -------------------------
        # PSEUDO
        # -------------------------
        ("button:visible", LocatorType.PSEUDO),
        ("input:hidden", LocatorType.PSEUDO),
        ("a:enabled", LocatorType.PSEUDO),
        ("span:disabled", LocatorType.PSEUDO),
        ("div:checked", LocatorType.PSEUDO),
        ("li:not(.active)", LocatorType.PSEUDO),
        # -------------------------
        # CSS SELECTORS
        # -------------------------
        ("div.class", LocatorType.CSS),
        ("#loginBtn", LocatorType.CSS),
        ("form[name=login]", LocatorType.CSS),
        ("input[type='text']", LocatorType.CSS),
        ("ul > li.item", LocatorType.CSS),
        ("button[data-role='x']", LocatorType.CSS),
        # HTML tag fallback -> CSS
        ("button", LocatorType.CSS),
        ("span", LocatorType.CSS),
        ("div", LocatorType.CSS),
        # -------------------------
        # ID/NAME fallback
        # -------------------------
        ("loginForm", LocatorType.ID),
        ("user_123", LocatorType.ID),
        ("NAME_001", LocatorType.ID),
        # -------------------------
        # UNKNOWN
        # -------------------------
        ("", LocatorType.UNKNOWN),
        ("   ", LocatorType.UNKNOWN),
        ("\n\t  ", LocatorType.UNKNOWN),
        ("!@#$%^", LocatorType.UNKNOWN),
        ("123 @bad", LocatorType.UNKNOWN),
        (None, LocatorType.UNKNOWN),
    ],
)
def test_locator_classifier_detect(locator, expected):
    assert LocatorClassifier.detect(locator) == expected
