from typing import Any, cast

from nrobo.locators.web_element_protocol import WebElementProtocol


class Locator(WebElementProtocol):
    """Playwright-style Locator with Selenium WebElement behavior + chaining.

    NOTE: All explicit methods delegate to SeleniumWrapper, which applies AutoWaitMixin.
    This guarantees waits/retries/scroll for every action.
    """

    _element: WebElementProtocol  # for IDE hints only

    def __init__(self, wrapper, locator: str, description: str | None = None):
        # Local import to avoid cycle at import time
        from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

        self.wrapper: SeleniumWrapper = cast(SeleniumWrapper, wrapper)
        self.locator = locator
        self.description = description or locator
        self.by, self.value = self.wrapper.resolve_locator(locator)

    # -------------------------------------------------------------------------
    # EXPLICIT METHODS (ensure IDE autocomplete + chaining)
    # These call wrapper methods, which use AutoWaitMixin under the hood.
    # -------------------------------------------------------------------------
    def click(self) -> "Locator":
        self.wrapper.click(self)
        return self

    def clear(self) -> "Locator":
        self.wrapper.clear(self)
        return self

    def send_keys(self, *value: Any) -> "Locator":
        self.wrapper.send_keys(self, *value)
        return self

    def submit(self) -> "Locator":
        self.wrapper.submit(self)
        return self

    def is_displayed(self) -> bool:
        return self.wrapper.is_displayed(self)

    @property
    def text(self) -> str:
        return self.wrapper.get_text(self)

    @property
    def tag_name(self) -> str:
        return self.wrapper.get_tag_name(self)

    def get_attribute(self, name: str) -> Any:
        return self.wrapper.get_attribute(self, name)

    def get_property(self, name: str) -> Any:
        return self.wrapper.get_property(self, name)

    def get_dom_attribute(self, name: str) -> Any:
        return self.wrapper.get_dom_attribute(self, name)

    def get_dom_property(self, name: str) -> Any:
        return self.wrapper.get_dom_property(self, name)

    def value_of_css_property(self, prop: str) -> str:
        return self.wrapper.value_of_css_property(self, prop)

    @property
    def location(self) -> dict:
        return self.wrapper.get_location(self)

    @property
    def location_once_scrolled_into_view(self) -> dict:
        return self.wrapper.get_location_scrolled(self)

    @property
    def size(self) -> dict:
        return self.wrapper.get_size(self)

    @property
    def rect(self) -> dict:
        return self.wrapper.get_rect(self)

    def screenshot(self, filename: str) -> bool:
        return self.wrapper.screenshot(self, filename)

    def screenshot_as_png(self) -> bytes:
        return self.wrapper.screenshot_as_png(self)

    def screenshot_as_base64(self) -> str:
        return self.wrapper.screenshot_as_base64(self)

    # Playwright-style sugar
    def fill(self, value: str) -> "Locator":
        self.clear().send_keys(value)
        return self

    def press(self, key: Any) -> "Locator":
        self.send_keys(key)
        return self

    # -------------------------------------------------------------------------
    # Dynamic fallback (for any WebElement method not explicitly declared)
    # -------------------------------------------------------------------------
    def __getattr__(self, name):
        el = self.wrapper._resolve(self)  # use mixin resolver
        attr = getattr(el, name)

        if callable(attr):

            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                return self if result is None else result

            return wrapper

        return attr
