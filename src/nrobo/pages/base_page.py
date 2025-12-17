# src/nrobo/pages/base_page.py

from __future__ import annotations

from typing import Union

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

try:
    from playwright.sync_api import Page as PlaywrightPage
except ImportError:
    PlaywrightPage = None  # Allow import even if Playwright isn't installed


class BasePage:
    """
    Base class for all Page Object Model (POM) classes in nRobo.
    Automatically initialized with either:
    - SeleniumWrapper (custom wrapper around Selenium WebDriver)
    - Playwright Page (sync API)
    """

    def __init__(self, page: Union[SeleniumWrapper, PlaywrightPage]):
        self.page = page

        # Handle SeleniumWrapper
        if isinstance(page, SeleniumWrapper):
            self.driver = page.driver
            self.logger = page.logger

        # Handle Playwright Page
        elif PlaywrightPage and isinstance(page, PlaywrightPage):
            self.driver = page  # For API parity, treat Playwright `Page` as `driver`
            self.logger = getattr(page, "logger", None)  # Optional, if attached

        else:
            raise TypeError(f"Unsupported page object type: {type(page)}")
