import time
from typing import Any, Callable, cast

from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.locators.web_element_protocol import WebElementProtocol


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

    DEFAULT_TIMEOUT = 10
    RETRY_STALE_ATTEMPTS = 3

    # ---------------------------------------------------------
    # Resolve (by,value,description) → WebElement (with wait + retry)
    # ---------------------------------------------------------
    def _resolve(self, locator) -> WebElementProtocol:
        by = locator.by
        value = locator.value
        description = locator.description

        for attempt in range(1, self.RETRY_STALE_ATTEMPTS + 1):
            try:
                print(f"[AutoWait] Resolving locator: {description!r}")
                element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.visibility_of_element_located((by, value)),
                    message=f"Timeout waiting for: {description!r}",
                )
                # Scroll into view (best-effort)
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                        element,
                    )
                except Exception:
                    print(f"[AutoWait] Scroll not critical for {description!r}")

                return cast(WebElementProtocol, element)

            except StaleElementReferenceException:
                print(
                    f"[AutoWait] StaleElement on attempt {attempt}/{self.RETRY_STALE_ATTEMPTS} for {description!r}"
                )
                if attempt == self.RETRY_STALE_ATTEMPTS:
                    raise
                time.sleep(0.2)

            except TimeoutException as e:
                print(f"[AutoWait] Timeout resolving: {description!r}")
                raise e

        raise RuntimeError(
            f"[AutoWait] Failed to resolve element: {description!r}"
        )  # pragma: no cover

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
