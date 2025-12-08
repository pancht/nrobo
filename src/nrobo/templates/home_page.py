import time

from selenium.webdriver.common.by import By

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


class PageHome(SeleniumWrapper):  # pylint: disable=R0901
    def __init__(
        self,
        wrapper: SeleniumWrapper,
    ):
        """constructor"""
        super().__init__(
            wrapper.driver,
            wrapper.logger,
        )
        # call parent constructor
        self.nrobo = wrapper
        self.driver = wrapper.driver
        self.logger = wrapper.logger

    # page elements
    txta_search = (By.NAME, "q")

    # page actions
    def search(self, keyword: str):
        self.logger.info(f"Search for {keyword}")
        self.nrobo.type_into(*self.txta_search, *keyword)
        time.sleep(5)

    def is_page_visible(self) -> bool:
        return self.nrobo.is_displayed(*self.txta_search)
