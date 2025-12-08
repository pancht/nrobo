from typing import Callable

from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.core import settings
from nrobo.helpers.logging_helper import get_logger
from nrobo.locators.locator import Locator

logger = get_logger(name=settings.NROBO_APP)


class AutoWaitMixin:
    """
    🔥 Automatically handles:
    - waits
    - retries
    - scroll into view
    - stale element recovery
    """

    DEFAULT_TIMEOUT = 10
    RETRY_STALE_ATTEMPTS = 3

    # ---------------------------------------------------------
    # 🔥 Resolve Locator to WebElement (auto-wait + stale retry)
    # ---------------------------------------------------------
    def _resolve(self, locator):
        _locator = Locator(locator)
        by = _locator.by
        value = _locator.value
        description = _locator.description

        for attempt in range(1, self.RETRY_STALE_ATTEMPTS + 1):
            try:
                logger.debug(f"[AutoWait] Resolving locator: {description}")

                element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.visibility_of_element_located((by, value)),
                    message=f"Timeout waiting for element: {description}",
                )

                # Scroll into view before returning
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                except Exception:
                    logger.debug(f"[AutoWait] Scroll failed but not fatal for {description}")

                return element

            except StaleElementReferenceException:
                logger.warning(
                    f"[AutoWait] StaleElementReferenceException on attempt {attempt}/{self.RETRY_STALE_ATTEMPTS} for {description}"
                )
                if attempt == self.RETRY_STALE_ATTEMPTS:
                    raise

            except TimeoutException as e:
                logger.error(f"[AutoWait] Timeout resolving element: {description}")
                raise e

        raise RuntimeError(f"Failed to resolve element: {description}")

    # ---------------------------------------------------------
    # 🔥 Generic action wrapper
    # ---------------------------------------------------------
    def _perform(self, locator, action: Callable):
        """
        Auto-resolve element and perform action safely.
        """
        element = self._resolve(locator)
        return action(element)

    # ---------------------------------------------------------
    # 🔥 ACTIONS (click, type, text)
    # ---------------------------------------------------------

    def click(self, locator):
        desc = locator.description
        logger.debug(f"[AutoWait] Clicking element: {desc}")

        return self._perform(locator, lambda el: el.click())

    def type(self, locator, text: str):
        desc = locator.description
        logger.debug(f"[AutoWait] Typing into element: {desc}")

        return self._perform(locator, lambda el: el.send_keys(text))

    def get_text(self, locator):
        desc = locator.description
        logger.debug(f"[AutoWait] Getting text from: {desc}")

        return self._perform(locator, lambda el: el.text)
