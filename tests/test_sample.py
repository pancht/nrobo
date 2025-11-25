from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass


def test_a(driver:NRoboSeleniumWrapperClass):
    driver.logger.info("HI")

def test_b(driver:NRoboSeleniumWrapperClass):
    driver.logger.info("BYE")