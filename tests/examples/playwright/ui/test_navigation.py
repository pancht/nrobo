from playwright.sync_api import Page, expect


def test_navigation_actions(page: Page):
    page.goto("https://the-internet.herokuapp.com")

    page.get_by_role("link", name="A/B Testing").click()

    expect(page.get_by_role("heading"), "A/B Test Variation 1").to_be_visible()

    page.go_back()

    expect(page.get_by_role("heading"), "Welcome to the-internet")

    page.go_forward()

    expect(page.get_by_role("heading"), "A/B Test Variation 1").to_be_visible()
