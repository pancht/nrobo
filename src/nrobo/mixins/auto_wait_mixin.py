import time
from typing import Any, Callable, cast

from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.core import settings
from nrobo.helpers.logging_helper import get_logger
from nrobo.helpers.selenium_helper import _safe_ready_state
from nrobo.protocols.web_element_protocol import WebElementProtocol
from nrobo.utils.driver_utils import is_mobile_session

logger = get_logger(name=settings.NROBO_APP)


class AutoWaitMixin:
    """
    Provides:
      - auto wait for visibility
      - scroll into view
      - stale element retries
      - tiny action wrapper
    Expectation:
      - `self.driver` exists (from SeleniumWrapperBase)
    """

    #
    # DEFAULT_TIMEOUT = 10
    # RETRY_STALE_ATTEMPTS = 3

    # ---------------------------------------------------------
    # Resolve (by,value,description) → WebElement (with wait + retry)
    # ---------------------------------------------------------
    def _resolve(self, locator) -> WebElementProtocol:
        by, value, desc = locator.by, locator.value, locator.description

        for attempt in range(1, settings.RETRY_STALE_ATTEMPTS + 1):
            try:
                logger.debug(f"[AutoWait] Resolving locator: {desc!r}")
                element = WebDriverWait(self.driver, settings.ELE_WAIT_TIMEOUT).until(
                    EC.visibility_of_element_located((by, value)),
                    message=f"Timeout waiting for: {desc!r}",
                )
                # Scroll into view (best-effort)
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                        element,
                    )
                except Exception:
                    logger.debug(f"[AutoWait] Scroll not critical for {desc!r}")

                return cast(WebElementProtocol, element)

            except StaleElementReferenceException:
                logger.debug(
                    f"[AutoWait] StaleElement on attempt {attempt}/{settings.RETRY_STALE_ATTEMPTS} for {desc!r}"
                )
                if attempt == settings.RETRY_STALE_ATTEMPTS:
                    raise
                time.sleep(0.2)

            except TimeoutException as e:
                logger.debug(f"[AutoWait] Timeout resolving: {desc!r}")
                raise e

        raise RuntimeError(f"[AutoWait] Failed to resolve element: {desc!r}")  # pragma: no cover

    # ---------------------------------------------------------
    # Generic action executor
    # ---------------------------------------------------------
    def _perform(self, locator, action: Callable[[WebElementProtocol], object]):
        el = self._resolve(locator)
        return action(el)

    def _wait_for_condition(
        self,
        locator,
        condition_fn: Callable[[Any], bool],
        timeout: int = 5,
        error_message: str = None,
    ):
        """
        Generic wait logic for conditions on resolved elements.
        Called by should_have_text(), should_be_visible(), etc.
        """
        end = time.time() + timeout

        last_exception = None

        while time.time() < end:
            try:
                element = self._resolve(locator)
                if condition_fn(element):
                    return locator
            except Exception as e:  # noqa
                last_exception = e

            time.sleep(0.2)

        # Timeout reached → fail with helpful message
        if error_message:
            raise AssertionError(error_message)  # pragma: no cover
        if last_exception:
            raise last_exception
        raise AssertionError("Condition not met within timeout")

    # ----------------- navigation helpers -----------------
    def _url(self):
        try:
            return self.driver.current_url
        except Exception:
            return ""

    def _maybe_wait_for_nav(self, before_url: str, pre_state: str | None, mode: str):
        """
        mode: 'none' (no wait), 'load' (always wait),
              'auto' (wait only if URL changed or readyState dropped)
        """
        if mode == "none" or is_mobile_session(self.driver):
            return

        if mode == "load":
            return self.wait_for_page_load()

        # auto-detect
        now_url = self._url()
        now_state = _safe_ready_state(self.driver)
        nav_detected = (now_url and now_url != before_url) or (
            pre_state == "complete" and now_state in ("loading", None)
        )
        if nav_detected:
            self.logger.debug("[AutoWait] navigation detected → waiting for load")
            self.wait_for_page_load()

    # ----------------- actions with integrated waits -----------------
    def get(self, url: str):
        self.goto(url=url)

    def goto(self, url: str, wait: str = "load"):
        """
        Navigate to URL, then optionally wait:
        - wait='load' (default): always wait for readyState 'complete'
        - wait='none': return immediately
        """
        self.logger.info(f"Go to: {url}")
        self.driver.get(url)
        self._maybe_wait_for_nav(
            before_url="", pre_state=None, mode="load" if wait != "none" else "none"
        )

    def click(self, locator, wait: str = "auto"):
        """
        Click element and optionally wait for navigation:
        - wait='auto' (default): wait only if nav likely occurred (URL changed or state fell to 'loading')
        - wait='load': always wait for full load after click
        - wait='none': never wait
        """
        desc = locator.description
        before_url = self._url()
        pre_state = _safe_ready_state(self.driver)

        el = self._resolve(locator)
        self.logger.debug(f"[AutoWait] click → {desc}")
        el.click()

        self._maybe_wait_for_nav(before_url, pre_state, wait)

        return locator

    def back(self, wait="auto"):
        before_url = self.driver.current_url
        pre_state = _safe_ready_state(self.driver)

        self.driver.back()

        self._maybe_wait_for_nav(before_url, pre_state, wait)

    def forward(self, wait="auto"):
        before_url = self.driver.current_url
        pre_state = _safe_ready_state(self.driver)

        self.driver.forward()
        self._maybe_wait_for_nav(before_url, pre_state, wait)

    def refresh(self, wait="auto"):
        before_url = self.driver.current_url
        pre_state = _safe_ready_state(self.driver)

        self.driver.refresh()
        self._maybe_wait_for_nav(before_url, pre_state, wait)
