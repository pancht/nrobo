import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
def test_navigation_actions(page: Page):
    # Open the application's main entry page and wait for the page to fully load
    # The navigation completes only after all critical resources are loaded,
    # with a maximum wait time of 30 seconds to ensure reliability
    page.goto("https://the-internet.herokuapp.com", wait_until="load", timeout=30000)

    # Identify the navigation link using its ARIA role and accessible label
    # Trigger a click action to move to the A/B Testing section of the site
    page.get_by_role("link", name="A/B Testing").click()

    # Block execution until the browser navigates to the A/B Testing URL
    # Confirms successful routing and waits for the DOM to be fully constructed
    # Times out after 10 seconds to prevent indefinite waits
    page.wait_for_url("**/abtest", timeout=10000, wait_until="domcontentloaded")

    # Validate that the current URL ends with "/abtest"
    # Uses a regular expression to remain flexible across environments
    expect(page).to_have_url(re.compile(r".*/abtest$"), timeout=10000)

    # Confirm that the page heading related to A/B Testing is visible
    # A partial match is used to allow dynamic heading variations
    expect(page.get_by_role("heading", name=re.compile(r"A\/B Test"))).to_be_visible()

    # Navigate backward in the browser history
    # This action should return the user to the application homepage
    page.go_back()

    # Assert that the homepage heading is visible after navigating back
    # Verifies correct handling of browser back navigation
    expect(page.get_by_role("heading", name="Welcome to the-internet")).to_be_visible()

    # Navigate forward in the browser history
    # Returns the browser to the previously visited A/B Testing page
    page.go_forward()

    # Re-validate that the A/B Testing heading is visible after forward navigation
    # Confirms browser history state is maintained correctly
    expect(page.get_by_role("heading", name=re.compile(r"A\/B Test"))).to_be_visible()

    # Assert that the current page title matches the expected value
    # Confirms that the browser has loaded the correct page and that
    # the document title reflects the intended application state
    expect(page).to_have_title("The Internet")

    # Navigate back to the homepage once again
    # Used to validate consistent navigation behavior across repeated actions
    page.go_back()

    # Ensure the homepage heading is visible after repeated navigation
    # Confirms UI state consistency and navigation stability
    expect(page.get_by_role("heading", name="Welcome to the-internet")).to_be_visible()

    # Reload the currently displayed page
    # Waits until the DOMContentLoaded event fires to ensure the DOM is ready
    page.reload(wait_until="domcontentloaded")
