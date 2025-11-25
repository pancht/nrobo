from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass


def test_launch_google(driver:NRoboSeleniumWrapperClass):
    driver.get("https://www.google.com")
    driver.logger.info("open url")