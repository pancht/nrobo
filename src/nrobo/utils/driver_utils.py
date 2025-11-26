# in e.g. utils/driver_utils.py
from selenium.webdriver.remote.webdriver import WebDriver


def is_mobile_session(driver: WebDriver) -> bool:
    """
    Returns True if the WebDriver
    session appears to be a mobile (Appium) session.
    """
    caps = getattr(driver, "capabilities", {}) or {}
    platform = caps.get("platformName")  # e.g., "Android", "iOS", or "Windows"
    # Check for mobile indicators
    if platform and platform.lower() in ("android", "ios"):
        return True
    # Some Appium sessions use deviceName, automationName
    if caps.get("deviceName") or caps.get("automationName"):
        return True
    return False
