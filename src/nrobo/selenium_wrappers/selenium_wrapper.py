import logging
import re
from pathlib import Path
from typing import Optional

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.core.settings import PAGE_LOAD_TIMEOUT
from nrobo.locators.has_selector_parser import HasSelectorParser
from nrobo.locators.has_text_selector_parser import HasTextEngine, HasTextParser
from nrobo.locators.locator import Locator
from nrobo.locators.locator_classifier import LocatorClassifier, LocatorType
from nrobo.locators.pseudo_selector_parser import PseudoSelectorParser
from nrobo.locators.text_selector_engine import TextSelectorEngine
from nrobo.mixins.auto_wait_mixin import AutoWaitMixin
from nrobo.mixins.window_mixin import WindowMixin
from nrobo.protocols.web_driver_protocol import SeleniumDriverProtocol
from nrobo.protocols.web_element_protocol import WebElementProtocol
from nrobo.selenium_wrappers.nrobo_types import AnyBy
from nrobo.selenium_wrappers.selenium_wrapper_base import SeleniumWrapperBase


class SeleniumWrapper(SeleniumWrapperBase, WindowMixin, AutoWaitMixin, SeleniumDriverProtocol):
    """Final Selenium wrapper:
    - driver delegation via SeleniumWrapperBase.__getattr__
    - window helpers from WindowMixin
    - auto-wait/stale/scroll from AutoWaitMixin
    - locator factory + element actions
    """

    driver: SeleniumDriverProtocol  # enables IDE autocompletion

    def __init__(self, driver: SeleniumDriverProtocol, logger: logging.Logger):
        super().__init__(driver, logger)
        self.driver: SeleniumDriverProtocol = driver
        self.logger = logger

    def _resolve_playwright_selector(self, locator: str):
        """
        Translates Playwright-style selectors to Selenium selectors.
        Supports:
            link=Text
            link:Partial
            text=Something
            "Quoted Text"
            'Quoted Text'
        """
        s = locator.strip()

        # ----------------------------------
        # 1. link=Exact text
        # ----------------------------------
        if s.startswith("link="):
            text = s.split("=", 1)[1].strip()
            return (By.LINK_TEXT, text)

        # ----------------------------------
        # 2. link:Partial text
        # ----------------------------------
        if s.startswith("link:"):
            text = s.split(":", 1)[1].strip()
            return (By.PARTIAL_LINK_TEXT, text)

        # ----------------------------------
        # 3. text=Something
        #    → JS-based text search (Playwright style)
        # ----------------------------------
        if s.startswith("text="):
            text = s.split("=", 1)[1].strip()
            return ("JS_TEXT", text)  # you handle JS_TEXT in locator._find()

        # ----------------------------------
        # 4. "Quoted Text"
        # ----------------------------------
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            text = s[1:-1]
            return ("JS_TEXT", text)

        # ----------------------------------
        # 5. Partial text: bareword (Playwright-like)
        # ----------------------------------
        # If contains whitespace & not CSS-like → treat as text search
        if " " in s and not re.search(r"[,>#\[\]:]", s):
            return ("JS_TEXT", s)

        # ----------------------------------
        # Fallback
        # ----------------------------------
        raise NotImplementedError(f"Unsupported Playwright selector: {locator}")

    # -------------------------------------------------------------------------
    # Locator resolution (string → (By, value))
    # -------------------------------------------------------------------------
    def resolve_locator(self, locator: str):
        loc_type = LocatorClassifier.detect(locator)

        if loc_type == LocatorType.XPATH:
            return By.XPATH, locator
        if loc_type == LocatorType.CSS:
            return By.CSS_SELECTOR, locator
        if loc_type == LocatorType.ID:
            return By.ID, locator
        if loc_type == LocatorType.NAME:
            return By.NAME, locator
        if loc_type == LocatorType.TEXT:
            return ("TEXT", locator)
        if loc_type == LocatorType.HAS_TEXT:
            base, text_value = HasTextParser.parse(locator)
            xpath = HasTextEngine.to_xpath(base, text_value)
            return (By.XPATH, xpath)
        if loc_type == LocatorType.PLAYWRIGHT:
            return self._resolve_playwright_selector(locator)
        # Fallback: treat as CSS
        return By.CSS_SELECTOR, locator

    # -------------------------------------------------------------------------
    # Public API: factory
    # -------------------------------------------------------------------------
    def locator(self, locator_string: str, description: str | None = None) -> Locator:
        return Locator(self, locator_string, description)

    def find_all(self, locator) -> list[WebElementProtocol]:
        """
        Raw find_elements without visibility wait.
        Caller can perform further checks.
        """
        try:
            return self.driver.find_elements(locator.by, locator.value)
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # Element ACTIONS (called by Locator; AutoWaitMixin used inside)
    # -------------------------------------------------------------------------
    def click(self, locator: Locator) -> None:
        self._resolve(locator).click()

    def clear(self, locator: Locator) -> None:
        self._resolve(locator).clear()

    def send_keys(self, locator: Locator, *value) -> None:
        self._resolve(locator).send_keys(*value)

    def submit(self, locator: Locator) -> None:
        self._resolve(locator).submit()

    # -------------------------------------------------------------------------
    # Element QUERIES / PROPERTIES
    # -------------------------------------------------------------------------
    def is_displayed(self, locator: Locator) -> bool:
        return self._resolve(locator).is_displayed()

    def get_text(self, locator: Locator) -> str:
        return self._resolve(locator).text

    def get_tag_name(self, locator: Locator) -> str:
        return self._resolve(locator).tag_name

    def get_attribute(self, locator: Locator, name: str):
        return self._resolve(locator).get_attribute(name)

    def get_property(self, locator: Locator, name: str):
        return self._resolve(locator).get_property(name)

    def get_dom_attribute(self, locator: Locator, name: str):
        return self._resolve(locator).get_dom_attribute(name)

    def get_dom_property(self, locator: Locator, name: str):
        return self._resolve(locator).get_dom_property(name)

    def value_of_css_property(self, locator: Locator, prop: str) -> str:
        return self._resolve(locator).value_of_css_property(prop)

    def get_location(self, locator: Locator) -> dict:
        return self._resolve(locator).location

    def get_location_scrolled(self, locator: Locator) -> dict:
        return self._resolve(locator).location_once_scrolled_into_view

    def get_size(self, locator: Locator) -> dict:
        return self._resolve(locator).size

    def get_rect(self, locator: Locator) -> dict:
        return self._resolve(locator).rect

    def screenshot(self, locator: Locator, filename: str) -> bool:
        return self._resolve(locator).screenshot(filename)

    def screenshot_as_png(self, locator: Locator) -> bytes:
        return self._resolve(locator).screenshot_as_png()

    def screenshot_as_base64(self, locator: Locator) -> str:
        return self._resolve(locator).screenshot_as_base64()

    # -------------------------------------------------------------------------
    # Existing utility (kept from your earlier code)
    # -------------------------------------------------------------------------
    def wait_for_element_to_be_present(
        self, by: AnyBy, value: Optional[str] = None, wait: int = 0
    ) -> bool:
        timeout = wait or PAGE_LOAD_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return True
        except Exception:
            return False

    def should_be_visible(self, locator, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: el.is_displayed(),
            timeout,
            error_message="Element not visible",
        )

    def should_have_text(self, locator, expected: str, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: expected in el.text,
            timeout,
            error_message=f"Element text did not contain {expected!r}",
        )

    def should_be_enabled(self, locator, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: el.is_enabled(),
            timeout,
            error_message="Element not enabled",
        )

    def should_be_disabled(self, locator, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: not el.is_enabled(),
            timeout,
            error_message="Element not disabled",
        )

    def should_contain_text(self, locator, substring: str, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: substring in (el.text or ""),
            timeout,
            error_message=f"Element text does not contain substring {substring!r}",
        )

    def should_not_be_visible(self, locator, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: not el.is_displayed(),
            timeout,
            "Element expected NOT to be visible",
        )

    def should_be_checked(self, locator, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: el.get_attribute("checked") in ("true", "checked", True, "1"),
            timeout,
            "Element expected to be checked",
        )

    def should_not_be_checked(self, locator, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: not el.get_attribute("checked"),
            timeout,
            "Element expected NOT to be checked",
        )

    def should_not_have_text(self, locator, unexpected, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: unexpected not in (el.text or ""),
            timeout,
            f"Element text should NOT contain {unexpected!r}",
        )

    def should_have_exact_text(self, locator, expected, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: (el.text or "").strip() == expected.strip(),
            timeout,
            f"Element text expected to equal {expected!r}",
        )

    def should_have_attribute(self, locator, name, expected, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: (el.get_attribute(name) or "").strip() == expected.strip(),
            timeout,
            f"Element attribute {name!r} expected to equal {expected!r}",
        )

    def should_have_property(self, locator, name, expected, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: el.get_property(name) == expected,
            timeout,
            f"Element property {name!r} expected to equal {expected!r}",
        )

    def should_have_value(self, locator, expected, timeout=5):
        return self.should_have_attribute(locator, "value", expected, timeout)

    def should_have_css(self, locator, prop_name, expected, timeout=5):
        return self._wait_for_condition(
            locator,
            lambda el: (el.value_of_css_property(prop_name) or "").strip() == expected.strip(),
            timeout,
            f"CSS property {prop_name!r} expected to equal {expected!r}",
        )

    def should_match_regex(self, locator, pattern, timeout=5):
        regex = re.compile(pattern)
        return self._wait_for_condition(
            locator,
            lambda el: bool(regex.search(el.text or "")),
            timeout,
            f"Element text expected to match regex {pattern!r}",
        )

    def _resolve_nth(self, locator, index: int) -> WebElementProtocol:
        """
        Resolve the nth element safely:
        - retry stale
        - ensure element exists
        - scroll into view
        """
        elements = self.find_all(locator)
        if len(elements) <= index:
            raise AssertionError(
                f"Element index {index} out of range. "
                f"Locator: {locator.description}, found: {len(elements)}"
            )

        # Now delegate to AutoWait for freshness + scroll
        el = elements[index]

        # Try stale-retry manually:
        for attempt in range(1, 4):
            try:
                # If element is displayed, scroll it
                if el.is_displayed():
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    except Exception:  # nosec: B110
                        pass
                    return el
            except StaleElementReferenceException:
                elements = self.find_all(locator)
                if len(elements) > index:
                    el = elements[index]
                else:
                    raise AssertionError(
                        f"Nth element vanished: index={index}, locator={locator.selector}"
                    )
        return el  # final fallback

    def count(self, locator) -> int:
        return len(self.find_all(locator))

    def _find_shadow(self, locator):
        from nrobo.locators.shadow_selector_parser import ShadowSelectorParser

        steps = ShadowSelectorParser.parse(locator.selector)

        script_path = Path(__file__).parent.parent / "locators/js/shadow_query.js"
        js = script_path.read_text()

        elements = self.driver.execute_script(js, steps)

        if not elements:
            raise AssertionError(f"No shadow DOM element found for {locator.selector}")

        # wrap nth logic
        if locator.index is not None:
            if locator.index >= len(elements):
                raise AssertionError(
                    f"Index {locator.index} out of range in Shadow DOM for {locator.selector}"
                )
            return elements[locator.index]

        return elements[0]  # single element behavior

    def _find_all_shadow(self, locator):
        from nrobo.locators.shadow_selector_parser import ShadowSelectorParser

        steps = ShadowSelectorParser.parse(locator.selector)

        script_path = Path(__file__).parent.parent / "locators/js/shadow_query.js"
        js = script_path.read_text()

        return self.driver.execute_script(js, steps) or []

    def _find_by_text(self, locator):
        # text=Login OR "Login"
        raw = locator.selector

        if raw.startswith("text="):
            text = raw.split("=", 1)[1]
        else:
            text = raw.strip("\"'")

        elements = TextSelectorEngine.find_by_text(self.driver, text)

        if not elements:
            raise AssertionError(f"No element found with visible text: {text!r}")

        if locator.index is not None:
            if locator.index >= len(elements):
                raise AssertionError(f"text selector nth index out of range for: {text!r}")
            return elements[locator.index]

        return elements[0]

    def _find_by_has_text(self, locator):
        # e.g. "button:has-text("Save")"
        loc = locator.selector

        css_selector, text_part = loc.split(":has-text(", 1)
        text = text_part.rstrip(")").strip("\"'")

        elements = TextSelectorEngine.find_has_text(self.driver, css_selector.strip(), text)

        if not elements:
            raise AssertionError(f"No element found for {css_selector} containing text {text!r}")

        if locator.index is not None:
            return elements[locator.index]

        return elements[0]

    def _find_all_by_text(self, locator):
        raw = locator.selector
        text = raw.split("=", 1)[1] if raw.startswith("text=") else raw.strip("\"'")
        return TextSelectorEngine.find_by_text(self.driver, text)

    def _find_all_by_has_text(self, locator):
        loc = locator.selector
        css_selector, text_part = loc.split(":has-text(", 1)
        text = text_part.rstrip(")").strip("\"'")
        return TextSelectorEngine.find_has_text(self.driver, css_selector.strip(), text)

    def _find_by_has(self, locator):
        base, inside = HasSelectorParser.split(locator.selector)

        js_path = Path(__file__).parent.parent / "locators/js/has_query.js"
        js = js_path.read_text()

        elements = self.driver.execute_script(js, base, inside)

        if not elements:
            raise AssertionError(f"No element found for selector {locator.selector!r}")

        # nth selection
        if locator.index is not None:
            if locator.index >= len(elements):
                raise AssertionError(f":has() nth index out of range for: {locator.selector}")
            return elements[locator.index]

        return elements[0]

    def _find_all_by_has(self, locator):
        base, inside = HasSelectorParser.split(locator.selector)

        js_path = Path(__file__).parent.parent / "locators/js/has_query.js"
        js = js_path.read_text()

        return self.driver.execute_script(js, base, inside) or []

    def _find_by_pseudo(self, locator):
        base, pseudos = PseudoSelectorParser.split(locator.selector)

        js_path = Path(__file__).parent.parent / "locators/js/pseudo_query.js"
        js = js_path.read_text()

        elements = self.driver.execute_script(js, base, pseudos)

        if not elements:
            raise AssertionError(f"No element found for pseudo selector {locator.selector}")

        if locator.index is not None:
            if locator.index >= len(elements):
                raise AssertionError(f"Index out of range for {locator.selector}")
            return elements[locator.index]

        return elements[0]

    def _find_all_by_pseudo(self, locator):
        base, pseudos = PseudoSelectorParser.split(locator.selector)

        js_path = Path(__file__).parent.parent / "locators/js/pseudo_query.js"
        js = js_path.read_text()

        return self.driver.execute_script(js, base, pseudos) or []

    # ---------------------------------------------------------------------------
    #
    # Playwright like methods in nrobo
    #
    # ---------------------------------------------------------------------------
    def goto(self, url: str, timeout: int = None):
        """Playwright-style navigation method."""
        if timeout:
            self.driver.set_page_load_timeout(timeout)

        self.driver.get(url)
        return self  # chainable, like Playwright

    def find_by_text(self, text: str):
        return TextSelectorEngine.find_by_text(self.driver, text)
