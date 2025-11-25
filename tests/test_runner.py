from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass


def test_launch_google(driver:NRoboSeleniumWrapperClass, logger):
    driver.get("https://www.google.com")
    logger.info("open url")
