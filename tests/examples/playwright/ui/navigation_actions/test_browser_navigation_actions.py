from playwright.sync_api import Page, expect


def test_navigation_actions(page: Page):
    # Navigate the browser to the application's main landing page
    # Wait until the full page load event is fired (all resources loaded),
    # with a maximum timeout of 30 seconds to ensure stable navigation
    page.goto("https://the-internet.herokuapp.com", wait_until="load", timeout=30000)

    # Locate the hyperlink element using ARIA role "link"
    # The link is identified by its accessible name "A/B Testing"
    # Then perform a click action to navigate to the A/B Testing page
    page.get_by_role("link", name="A/B Testing").click()

    # Wait until the browser URL matches the expected A/B testing page pattern
    # Ensures navigation has completed and the DOM content is fully loaded,
    # with a maximum wait time of 10 seconds to avoid indefinite blocking
    page.wait_for_url("**/abtest", timeout=10000, wait_until="domcontentloaded")

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
