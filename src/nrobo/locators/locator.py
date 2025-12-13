import re
from typing import Any, Callable, cast

from nrobo.core import settings
from nrobo.helpers.logging_helper import get_logger
from nrobo.locators.locator_classifier import LocatorClassifier, LocatorType
from nrobo.protocols.web_element_protocol import WebElementProtocol

logger = get_logger(name=settings.NROBO_APP)


class Locator(WebElementProtocol):
    """Playwright-style Locator with Selenium WebElement behavior + chaining.

    NOTE: All explicit methods delegate to SeleniumWrapper, which applies AutoWaitMixin.
    This guarantees waits/retries/scroll for every action.
    """

    _element: WebElementProtocol  # for IDE hints only

    def __init__(
        self,
        wrapper,
        locator: str,
        description: str | None = None,
        *,
        parent: "Locator" = None,
    ):
        # Local import to avoid cycle at import time
        from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

        self.parent = parent  # chain support

        self.wrapper: SeleniumWrapper = cast(SeleniumWrapper, wrapper)
        self.selector = locator
        self.locator_type = LocatorClassifier.detect(locator)
        self.description = description or locator
        self.index = None  # means "single element"
        self.multiple = False  # helps distinguish single vs multiple retrieval

        # Ensure all methods like filter(), all(), nth() can access by/value without triggering __getattr__
        self.by, self.value = self.wrapper.resolve_locator(locator)

        self.is_shadow = ">>>" in locator or "shadow::" in locator

    @property
    def full_selector(self) -> str:
        if not self.parent:
            return self.selector

        parent = self.parent.full_selector
        child = self.selector

        # --- 1. XPath chaining rules ---
        if self.locator_type == LocatorType.XPATH:
            # Absolute XPath overrides parent
            if child.startswith("//") or child.startswith("/"):
                return child

            # Remove optional leading .//
            if child.startswith(".//"):
                child = child[3:]
            elif child.startswith("./"):
                child = child[2:]

            return f"{parent}//{child}"

        # --- 2. Shadow DOM chaining ---
        if ">>>" in parent or ">>>" in child:
            return f"{parent} >>> {child}"

        # --- 3. CSS pseudo selectors applied to parent ---
        if child.startswith(":"):
            return f"{parent}{child}"

        # --- 4. Direct combinator selectors ---
        if child.startswith((">", "+", "~", "[")):
            return f"{parent}{child}"

        # --- 5. Default CSS descendant ---
        return f"{parent} {child}"

    # -------------------------------------------------------------------------
    # Playwright-style chaining: locator("CSS").locator("text=Login") etc.
    # Each segment must be re-classified as a fresh selector.
    # -------------------------------------------------------------------------
    def locator(self, selector: str) -> "Locator":
        """
        Creates a new Locator based on the given selector, independent of the
        parent locator type. This enables playwright-style chaining:
            page.locator("div").locator(":visible").locator("text=Login")
        """
        from nrobo.locators.locator import Locator  # local import to avoid cyclic

        # Construct a new Locator, inheriting wrapper but NOT inheriting parent's by/value
        new_loc = Locator(self.wrapper, selector, f"{self.description} >> {selector}")
        return new_loc

    def _maybe_chain(self):
        from nrobo.core import settings

        return self if settings.ENABLE_LOCATOR_ACTION_CHAINING else None

    # -------------------------------------------------------------------------
    # EXPLICIT METHODS (ensure IDE autocomplete + chaining)
    # These call wrapper methods, which use AutoWaitMixin under the hood.
    # -------------------------------------------------------------------------
    def click(self) -> "Locator":
        self.wrapper.click(self)
        return self._maybe_chain()

    def clear(self) -> "Locator":
        self.wrapper.clear(self)
        return self._maybe_chain()

    def send_keys(self, *value: Any) -> "Locator":
        self.wrapper.send_keys(self, *value)
        return self._maybe_chain()

    def submit(self) -> "Locator":
        self.wrapper.submit(self)
        return self._maybe_chain()

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
        return self._maybe_chain()

    def press(self, key: Any) -> "Locator":
        self.send_keys(key)
        return self._maybe_chain()

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

        return attr  # pragma: no cover

    def _find(self) -> WebElementProtocol:
        """
        Fetch element:
        - Resolve the entire selector chain (`full_selector`)
        - Dispatch based on locator type (TEXT, HAS, PSEUDO, SHADOW, etc.)
        - Support nth() and auto-wait
        """

        # Resolve final full selector WITHOUT mutating self
        by, value = self.wrapper.resolve_locator(self.full_selector)

        # SHADOW DOM
        if ">>>" in self.full_selector or "shadow::" in self.full_selector:
            return self.wrapper._find_shadow(self)

        # Playwright-style selector handlers
        if by == "TEXT":
            return self.wrapper._find_by_text(self)

        if by == "HAS_TEXT":
            return self.wrapper._find_by_has_text(self)

        if by == "HAS":
            return self.wrapper._find_by_has(self)

        if by == "PSEUDO":
            return self.wrapper._find_by_pseudo(self)

        if by == "JS_TEXT":
            return self.wrapper.find_by_text(value)

        # Nth element
        if self.index is not None:
            return self.wrapper._resolve_nth(by, value, self.index)

        # Default: auto-wait resolve for single element
        return self.wrapper._resolve_with(by, value)

    def should_be_visible(self, timeout=5) -> "Locator":
        self.wrapper.should_be_visible(self, timeout)
        return self._maybe_chain()

    def should_have_text(self, expected: str, timeout=5) -> "Locator":
        self.wrapper.should_have_text(self, expected, timeout)
        return self._maybe_chain()

    def should_be_enabled(self, timeout=5) -> "Locator":
        self.wrapper.should_be_enabled(self, timeout)
        return self._maybe_chain()

    def should_be_disabled(self, timeout=5) -> "Locator":
        self.wrapper.should_be_disabled(self, timeout)
        return self._maybe_chain()

    def should_contain_text(self, substring: str, timeout=5) -> "Locator":
        self.wrapper.should_contain_text(self, substring, timeout)
        return self._maybe_chain()

    def should_not_be_visible(self, timeout=5) -> "Locator":
        self.wrapper.should_not_be_visible(self, timeout)
        return self._maybe_chain()

    def should_be_checked(self, timeout=5) -> "Locator":
        self.wrapper.should_be_checked(self, timeout)
        return self._maybe_chain()

    def should_not_be_checked(self, timeout=5) -> "Locator":
        self.wrapper.should_not_be_checked(self, timeout)
        return self._maybe_chain()

    def should_not_have_text(self, unexpected, timeout=5) -> "Locator":
        self.wrapper.should_not_have_text(self, unexpected, timeout)
        return self._maybe_chain()

    def should_have_exact_text(self, expected, timeout=5) -> "Locator":
        self.wrapper.should_have_exact_text(self, expected, timeout)
        return self._maybe_chain()

    def should_have_attribute(self, name, expected, timeout=5) -> "Locator":
        self.wrapper.should_have_attribute(self, name, expected, timeout)
        return self._maybe_chain()

    def should_have_property(self, name, expected, timeout=5) -> "Locator":
        self.wrapper.should_have_property(self, name, expected, timeout)
        return self._maybe_chain()

    def should_have_value(self, expected, timeout=5) -> "Locator":
        self.wrapper.should_have_value(self, expected, timeout)
        return self._maybe_chain()

    def should_have_css(self, prop, expected, timeout=5) -> "Locator":
        self.wrapper.should_have_css(self, prop, expected, timeout)
        return self._maybe_chain()

    def should_match_regex(self, pattern, timeout=5) -> "Locator":
        self.wrapper.should_match_regex(self, pattern, timeout)
        return self._maybe_chain()

    def all(self) -> "LocatorCollection":  # noqa: F821
        """
        Return list of Locators for all matching elements.
        Each Locator has an index assigned.
        """
        if self.is_shadow:
            elements = self.wrapper._find_all_shadow(self)
        elif self.by == "TEXT":
            elements = self.wrapper._find_all_by_text(self)
        elif self.by == "HAS_TEXT":
            elements = self.wrapper._find_all_by_has_text(self)
        elif self.by == "HAS":
            elements = self.wrapper._find_all_by_has(self)
        elif self.by == "PSEUDO":
            elements = self.wrapper._find_all_by_pseudo(self)
        else:
            elements = self.wrapper.find_all(self)

        locators = []

        for i, _ in enumerate(elements):
            new_loc = Locator(
                self.wrapper,
                self.selector,
                f"{self.description}[{i}]",
                parent=self.parent,  # preserve chain
            )
            new_loc.by = self.by
            new_loc.value = self.value
            new_loc.index = i
            locators.append(new_loc)

        from nrobo.locators.locator_collection import LocatorCollection

        return LocatorCollection(locators)

    def filter(
        self,
        has_text: str | None = None,
        has_not_text: str | None = None,
        has_attribute: tuple[str, str] | None = None,
        has_regex: str | None = None,
        has: Callable[[WebElementProtocol], bool] | None = None,
    ) -> "LocatorCollection":  # noqa: F821
        """
        Filter all matching elements using conditions:
        - has_text="Login"
        - has_not_text="Error"
        - has_attribute=("role", "button")
        - has_regex=r"User \\d+"  # noqa: W605
        - has=lambda el: custom condition
        """

        elements = self.wrapper.find_all(self)
        results = []

        regex = re.compile(has_regex) if has_regex else None

        for index, el in enumerate(elements):
            try:
                text = el.text or ""
            except Exception:  # pragma: no cover
                text = ""

            # Condition checks
            if has_text and has_text not in text:
                continue

            if has_not_text and has_not_text in text:
                continue

            if has_attribute:
                attr_name, attr_value = has_attribute
                if (el.get_attribute(attr_name) or "") != attr_value:
                    continue  # pragma: no cover

            if regex and not regex.search(text):
                continue

            if has and not has(el):
                continue

            # Passed all filters — create new Locator
            new_loc = Locator(
                self.wrapper,
                self.selector,
                f"{self.description}[filtered:{index}]",
                parent=self.parent,  # preserve full chain
            )
            new_loc.by = self.by
            new_loc.value = self.value
            new_loc.index = index
            results.append(new_loc)

        return results

    def first_filtered(self, **kwargs) -> "Locator":
        filtered = self.filter(**kwargs)
        if not filtered:
            raise AssertionError(f"No elements found after filtering: {kwargs}")
        return filtered[0]

    def last_filtered(self, **kwargs) -> "Locator":
        filtered = self.filter(**kwargs)
        if not filtered:
            raise AssertionError(f"No elements found after filtering: {kwargs}")  # pragma: no cover
        return filtered[-1]

    def nth(self, index: int) -> "Locator":
        """
        Return Locator for nth matching element.
        """
        new_loc = Locator(
            self.wrapper, self.selector, f"{self.description}[{index}]", parent=self.parent
        )
        new_loc.by = self.by
        new_loc.value = self.value
        new_loc.index = index
        return new_loc

    def first(self) -> "Locator":
        """
        Return the first matching element, preserving full selector chain.
        """
        new_loc = Locator(
            wrapper=self.wrapper,
            locator=self.selector,
            description=f"{self.description}[first]",
            parent=self.parent,
        )
        new_loc.by, new_loc.value = self.wrapper.resolve_locator(new_loc.full_selector)
        new_loc.index = 0
        return new_loc

    def last(self) -> "Locator":
        """
        Return the last matching element, preserving full selector chain.
        """
        count = self.count()
        if count == 0:
            raise AssertionError(
                f"No elements found for locator {self.full_selector}"
            )  # pragma: no cover

        new_loc = Locator(
            wrapper=self.wrapper,
            locator=self.selector,
            description=f"{self.description}[last]",
            parent=self.parent,
        )
        new_loc.by, new_loc.value = self.wrapper.resolve_locator(new_loc.full_selector)
        new_loc.index = count - 1
        return new_loc

    def count(self) -> int:
        """
        Count all elements matching the full selector chain.
        """
        return len(self.wrapper.find_all(self))
