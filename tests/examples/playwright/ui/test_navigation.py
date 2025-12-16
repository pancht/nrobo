from playwright.async_api import Page


def test_open_pypi(page: Page):
    page.goto("https://google.com")
