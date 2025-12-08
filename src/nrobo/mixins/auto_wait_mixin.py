import time
from typing import Callable, cast

from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.core import settings
from nrobo.helpers.logging_helper import get_logger
from nrobo.locators.web_element_protocol import WebElementProtocol

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
                logger.debug(f"[AutoWait] Resolving locator: {description!r}")
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
                    logger.debug(f"[AutoWait] Scroll not critical for {description!r}")

                return cast(WebElementProtocol, element)

            except StaleElementReferenceException:
                logger.warning(
                    f"[AutoWait] StaleElement on attempt {attempt}/{self.RETRY_STALE_ATTEMPTS} for {description!r}"
                )
                if attempt == self.RETRY_STALE_ATTEMPTS:
                    raise
                time.sleep(0.2)

            except TimeoutException as e:
                logger.error(f"[AutoWait] Timeout resolving: {description!r}")
                raise e

        raise RuntimeError(f"[AutoWait] Failed to resolve element: {description!r}")

    # ---------------------------------------------------------
    # Generic action executor
    # ---------------------------------------------------------
    def _perform(self, locator, action: Callable[[WebElementProtocol], object]):
        el = self._resolve(locator)
        return action(el)
