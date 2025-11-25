from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass
class TestClassA:
    def test_a(self, driver:NRoboSeleniumWrapperClass):
        driver.logger.info("HI")
        pass