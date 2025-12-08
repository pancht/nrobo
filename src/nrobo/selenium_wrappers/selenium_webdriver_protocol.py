from typing import Protocol

from selenium.webdriver.remote.webdriver import WebDriver


class SeleniumDriverProtocol(Protocol):
    """Protocol describing the driver methods available to the wrapper."""

    # Inherit full Selenium WebDriver API
    pass


# Optionally: declare driver must be a real WebDriver too
class SeleniumTypedDriver(WebDriver, SeleniumDriverProtocol):
    pass
