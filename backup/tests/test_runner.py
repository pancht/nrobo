from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass


def test_launch_google_failure(driver:NRoboSeleniumWrapperClass, logger):
    driver.get("https://www.google.com")
    logger.info("open url")
    assert False


def test_launch_google_success(driver:NRoboSeleniumWrapperClass, logger):
    driver.get("https://www.google.com")
    logger.info("open url")


