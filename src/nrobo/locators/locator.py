from typing import Any

from nrobo.locators.web_element_protocol import WebElementProtocol


class Locator(WebElementProtocol):
    """Playwright-style Locator with Selenium WebElement behavior + chaining."""

    _element: WebElementProtocol

    def __init__(self, wrapper, locator: str, description: str = None):
        from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

        self.wrapper: SeleniumWrapper = wrapper
        self.locator = locator
        self.description = description or locator
        self.by, self.value = self.wrapper.resolve_locator(locator)

    # -------------------------------------------------------------------------
    # Internal Helper
    # -------------------------------------------------------------------------
    def _find(self) -> WebElementProtocol:
        """Fetch the underlying Selenium WebElement each time."""

        return self.wrapper.find_element(self.by, self.value)

    # -------------------------------------------------------------------------
    # AUTOCOMPLETE-ENABLED EXPLICIT WRAPPER METHODS
    # -------------------------------------------------------------------------

    # --- Core Actions ---
    def click(self) -> "Locator":
        self._find().click()
        return self

    def clear(self) -> "Locator":
        self._find().clear()
        return self

    def send_keys(self, *value: Any) -> "Locator":
        self._find().send_keys(*value)
        return self

    def submit(self) -> "Locator":
        self._find().submit()
        return self

    # --- Visibility & State ---
    def is_displayed(self) -> bool:
        return self._find().is_displayed()

    def is_enabled(self) -> bool:
        return self._find().is_enabled()

    def is_selected(self) -> bool:
        return self._find().is_selected()

    # --- Text & Tag ---
    @property
    def text(self) -> str:
        return self._find().text

    @property
    def tag_name(self) -> str:
        return self._find().tag_name

    # --- DOM Access ---
    def get_attribute(self, name: str) -> Any:
        return self._find().get_attribute(name)

    def get_property(self, name: str) -> Any:
        return self._find().get_property(name)

    def get_dom_attribute(self, name: str) -> Any:
        return self._find().get_dom_attribute(name)

    def get_dom_property(self, name: str) -> Any:
        return self._find().get_dom_property(name)

    # --- CSS ---
    def value_of_css_property(self, prop: str) -> str:
        return self._find().value_of_css_property(prop)

    # --- Layout ---
    @property
    def location(self) -> dict:
        return self._find().location

    @property
    def location_once_scrolled_into_view(self) -> dict:
        return self._find().location_once_scrolled_into_view

    @property
    def size(self) -> dict:
        return self._find().size

    @property
    def rect(self) -> dict:
        return self._find().rect

    # --- Screenshots ---
    def screenshot(self, filename: str) -> bool:
        return self._find().screenshot(filename)

    def screenshot_as_png(self) -> bytes:
        return self._find().screenshot_as_png()

    def screenshot_as_base64(self) -> str:
        return self._find().screenshot_as_base64()

    # --- Child Locators ---
    def find_element(self, by: str, value: str) -> WebElementProtocol:
        return self._find().find_element(by, value)

    def find_elements(self, by: str, value: str):
        return self._find().find_elements(by, value)

    # -------------------------------------------------------------------------
    # ADVANCED LOCATOR-SPECIFIC FLUENT METHODS
    # -------------------------------------------------------------------------
    def fill(self, value: str) -> "Locator":
        elem = self._find()
        elem.clear()
        elem.send_keys(value)
        return self

    def press(self, key: Any) -> "Locator":
        self._find().send_keys(key)
        return self

    # -------------------------------------------------------------------------
    # Dynamic fallback for any WebElement method not explicitly declared
    # -------------------------------------------------------------------------
    def __getattr__(self, name):
        elem = self._find()
        attr = getattr(elem, name)

        if callable(attr):

            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                return self if result is None else result

            return wrapper

        return attr
