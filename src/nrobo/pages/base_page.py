# src/nrobo/pages/base_page.py

from __future__ import annotations

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


class BasePage:
    """
    Base class for all Page Object Model (POM) classes in nRobo.
    Automatically initialized with the `page` fixture (SeleniumWrapper).
    """

    def __init__(self, page: SeleniumWrapper):
        self.page = page  # nRobo SeleniumWrapper instance
        self.driver = page.driver  # underlying Selenium WebDriver
        self.logger = page.logger  # unified per-test logger
