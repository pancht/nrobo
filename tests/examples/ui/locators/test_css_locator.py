import pytest

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

website = "https://the-internet.herokuapp.com/"
expected_header = "Welcome to the-internet"


@pytest.mark.example
def test_css_selector_strategies(page: SeleniumWrapper):
    # Log the action for debugging and clarity
    page.logger.info(f"Go to site: {website}")

    # Navigate the browser to the target URL
    page.goto(website)

    # Locate the <h1> header element and assert its exact text value
    page.locator("h1").should_have_exact_text(expected_header)

    # Locate and click a hyperlink using a CSS attribute selector:
    #   a[href='/add_remove_elements/']
    # After clicking, chain another locator to find the button inside #content > div
    # Finally, assert that the located button is visible on the page
    page.locator("a[href='/add_remove_elements/']").click().locator(
        "#content > div > button"
    ).should_be_visible()

    # Locate a <button> element that contains the visible text "Element" anywhere inside it.
    # The ':has-text()' pseudo-class is a Playwright-style extension (not standard CSS),
    # supported by nRoBo to filter elements by their inner text content.
    # Finally, assert that the button is visible on the page.
    page.locator('button:has-text("Element")').should_be_visible()

    # Navigate one step back in browser history (equivalent to pressing the browser's back button)
    page.back()

    # After navigating back, verify that the element with class "heading" has the expected text
    # This ensures that the correct page content is restored after navigation
    page.locator(".heading").should_have_exact_text(expected_header)

    # Locate the element with ID 'page-footer' and assert that it is visible
    # This confirms that the footer is properly rendered and accessible in the viewport
    page.locator("#page-footer").should_be_visible()

    # Verify that the page section with the CSS selector "div.row" is visible.
    # This ensures that the main row container is correctly rendered on the page.
    page.locator("div.row").should_be_visible()

    # Validate that the link pointing to the "Add/Remove Elements" page is visible.
    # Using an attribute selector ensures the correct link is targeted by its href value.
    page.locator("a[href='/add_remove_elements/']").should_be_visible()

    # Click on the "Checkboxes" link to navigate to that page.
    # Then, chain a new locator to find checkbox inputs (input[type=checkbox]).
    # Finally, assert that the checkboxes are visible on the page.
    page.locator("a[href='/checkboxes']").click().locator(
        "input[type=checkbox]"
    ).should_be_visible()

    # Navigate one step back in the browser’s history.
    # This confirms that navigation works as expected and returns to the previous page.
    page.back()

    # Verify that the link with an exact href attribute match to '/checkboxes' is visible on the page.
    # This ensures the specific navigation link to the "Checkboxes" section is rendered correctly.
    page.locator("a[href='/checkboxes']").should_be_visible()

    # Verify that a link whose href attribute STARTS WITH '/check' is visible.
    # The ^= operator is a CSS "starts with" selector — useful for matching partial or dynamic URLs.
    page.locator("a[href^='/check']").should_be_visible()

    # Verify that a link whose href attribute ENDS WITH 'boxes' is visible.
    # The $= operator is a CSS "ends with" selector, often used for matching URL suffixes.
    page.locator("a[href$='boxes']").should_be_visible()

    # Verify that a link whose href attribute CONTAINS the substring 'box' is visible.
    # The *= operator is a CSS "contains" selector, allowing flexible pattern matching in attributes.
    page.locator("a[href*='box']").should_be_visible()

    # Locate any anchor (<a>) element that is a **descendant** (at any depth) of a <div> element.
    # This matches <div><span><a></a></span></div> as well as <div><a></a></div>
    page.locator("div a").should_be_visible()

    # Locate an anchor (<a>) element that is a **direct child** of a <div> element.
    # This matches <div><a></a></div> but NOT <div><span><a></a></span></div>
    page.locator("div > a")

    # Locate the first <ul> element that immediately follows an <h2> (adjacent sibling)
    # This verifies that the heading is followed by a list, commonly used for navigation or grouped content
    page.locator("h2 + ul").should_be_visible()

    # Locate the first <ul> element that is a general sibling of <h1> (not necessarily adjacent)
    # Ensures there's a list that shares the same parent with the <h1>, validating page layout structure
    page.locator("h1 ~ ul").should_be_visible()

    # Select the first list item in an unordered list using :nth-child(1)
    # Useful to verify ordered content such as menus, bullet lists, or ordered steps
    page.locator("ul li:nth-child(1)").should_be_visible()

    # Click on the "Tables" link, then locate the second <tr> (table row) using :nth-of-type
    # Asserts that a specific row in the table is rendered correctly and accessible
    page.locator("a[href='/tables']").click().locator("tr:nth-of-type(2)").should_be_visible()

    # Navigate back to the previous page after interacting with the table
    page.back()

    # Select the last list item inside a <ul> using the CSS :last-child selector
    # Confirms full list rendering and edge elements are visible
    page.locator("ul li:last-child").should_be_visible()

    # Locate an <h2> with the exact visible text "Examples" using :has-text
    # Ensures section headers are visible and correctly labeled
    page.locator('h2:has-text("Examples")').should_be_visible()

    # Locate a link (<a>) with the visible text "A/B Testing" using :has-text
    # Confirms the presence of key navigation links or content references
    page.locator('a:has-text("A/B Testing")').should_be_visible()

    # Click the "Inputs" link, then locate a <div> that contains an input[type='number'] using :has()
    # This verifies both the navigation and the correct input field structure
    page.locator("a[href='/inputs']").click().locator(
        "div:has(input[type='number'])"
    ).should_be_visible()

    # Navigate back to the previous page after checking the inputs
    page.back()

    # currently not supported
    # page.locator("li:has(a:has-text('Checkboxes'))").should_be_visible()
