from playwright.sync_api import Page, expect


def test_navigation_actions(page: Page):
    # Navigate the browser to the main landing page of the test application
    # This loads the homepage and waits until the navigation is complete
    page.goto("https://the-internet.herokuapp.com")

    # Locate the hyperlink element using ARIA role "link"
    # The link is identified by its accessible name "A/B Testing"
    # Then perform a click action to navigate to the A/B Testing page
    page.get_by_role("link", name="A/B Testing").click()

    # Assert that the heading element on the destination page is visible
    # This verifies that the navigation to the A/B Testing page was successful
    # The expected heading text is "A/B Test Variation 1"
    expect(page.get_by_role("heading", name="A/B Test Variation 1")).to_be_visible()

    # Navigate one step backward in the browser history
    # This should take the user back to the homepage
    page.go_back()

    # Verify that the homepage heading is visible after navigating back
    # Confirms correct browser back navigation behavior
    expect(page.get_by_role("heading", name="Welcome to the-internet")).to_be_visible()

    # Navigate one step forward in the browser history
    # This should return the user to the A/B Testing page again
    page.go_forward()

    # Assert that the A/B Testing page heading is visible again
    # Confirms correct browser forward navigation behavior
    expect(page.get_by_role("heading", name="A/B Test Variation 1")).to_be_visible()

    # Navigate back once more to the homepage
    # Used to validate repeated navigation stability
    page.go_back()

    # Verify that the homepage heading is visible again
    # Ensures state consistency after multiple navigation actions
    expect(page.get_by_role("heading", name="Welcome to the-internet")).to_be_visible()

    # Reload the current page
    # The reload waits until the DOMContentLoaded event fires,
    # ensuring the DOM is fully parsed before continuing
    page.reload(wait_until="domcontentloaded")
