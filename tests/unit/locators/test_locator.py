from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from nrobo.locators.locator import Locator
from nrobo.locators.locator_classifier import LocatorType

# ---------------------
#  Fixtures / Mocks
# ---------------------


@pytest.fixture
def fake_element():
    """Simple fake WebElementProtocol-like"""
    el = SimpleNamespace()
    el.text = "Hello World"
    el.get_attribute = Mock(return_value="btn")
    el.get_property = Mock(return_value="propVal")
    return el


@pytest.fixture
def fake_wrapper(fake_element):
    w = Mock()
    # basic resolve_locator
    w.resolve_locator.side_effect = lambda selector: ("BY", selector)
    # basic find_all
    w.find_all.return_value = [fake_element, fake_element]
    # find
    w._resolve_with.return_value = fake_element
    # text find
    w._find_by_text.return_value = fake_element
    return w


# ---------------------
#  Basic Locator Behavior
# ---------------------


def test_full_selector_no_parent(fake_wrapper):
    loc = Locator(fake_wrapper, "div")
    assert loc.full_selector == "div"


def test_full_selector_xpath_chaining(fake_wrapper):
    parent = Locator(fake_wrapper, "//parent")
    child = Locator(fake_wrapper, "child", parent=parent)
    child.locator_type = LocatorType.XPATH

    # child doesn't start with slash
    assert child.full_selector == "//parent//child"

    # absolute child
    child2 = Locator(fake_wrapper, "/root", parent=parent)
    child2.locator_type = LocatorType.XPATH
    assert child2.full_selector == "/root"


def test_full_selector_shadow_chaining(fake_wrapper):
    p = Locator(fake_wrapper, "root >>> child1")
    c = Locator(fake_wrapper, "child2", parent=p)
    assert ">>>" in c.full_selector and "child2" in c.full_selector


def test_full_selector_css_pseudo_and_combinators(fake_wrapper):
    p = Locator(fake_wrapper, "div")
    for child in [":hover", "> span", "+ span", "~ span", "[data-test]"]:
        loc = Locator(fake_wrapper, child, parent=p)
        assert loc.full_selector.startswith("div")


def test_locator_returns_new_locator(fake_wrapper):
    base = Locator(fake_wrapper, "div")
    nxt = base.locator("span")
    assert nxt.selector == "span"
    assert nxt.description.endswith(">> span")


# ---------------------
#  Explicit action methods
# ---------------------


def test_click_clear_send_keys_submits_chain(fake_wrapper):
    loc = Locator(fake_wrapper, "input")
    assert loc.click() is loc
    assert loc.clear() is loc
    assert loc.send_keys("val") is loc
    assert loc.submit() is loc


# ---------------------
#  Properties & Wrapper Delegation
# ---------------------


def test_properties_delegate(fake_wrapper):
    loc = Locator(fake_wrapper, "elem")
    assert loc.is_displayed() == fake_wrapper.is_displayed(loc)
    assert loc.text == fake_wrapper.get_text(loc)
    assert loc.tag_name == fake_wrapper.get_tag_name(loc)


def test_attributes_properties_and_css(fake_wrapper):
    loc = Locator(fake_wrapper, "elem")
    assert loc.get_attribute("a") == fake_wrapper.get_attribute(loc, "a")
    assert loc.get_property("p") == fake_wrapper.get_property(loc, "p")
    assert loc.value_of_css_property("c") == fake_wrapper.value_of_css_property(loc, "c")


# ---------------------
#  _find Resolution
# ---------------------


def test_find_text_locator(fake_wrapper):
    fake_wrapper.resolve_locator.side_effect = lambda s: ("TEXT", s)
    loc = Locator(fake_wrapper, "text=foo")
    assert loc._find() == fake_wrapper._find_by_text(loc)


def test_find_shadow_locator(fake_wrapper):
    loc = Locator(fake_wrapper, "a >>> b")
    fake_wrapper._find_shadow.return_value = "shadow"
    assert loc._find() == "shadow"


def test_find_default(fake_wrapper):
    loc = Locator(fake_wrapper, "x")
    assert loc._find() == fake_wrapper._resolve_with("BY", "x")


# ---------------------
#  should_* Behavior
# ---------------------


@pytest.mark.parametrize(
    "method,args",
    [
        ("should_be_visible", ()),
        ("should_have_text", ("txt",)),
        ("should_be_enabled", ()),
        ("should_not_be_visible", ()),
        ("should_contain_text", ("txt",)),
        ("should_match_regex", (r".*",)),
    ],
)
def test_should_methods_chain(fake_wrapper, method, args):
    loc = Locator(fake_wrapper, "el")
    result = getattr(loc, method)(*args)
    assert result is loc


# ---------------------
#  all(), nth(), first(), last(), count()
# ---------------------


def test_all_returns_collection(fake_wrapper):
    loc = Locator(fake_wrapper, "els")
    coll = loc.all()
    # should produce 2 elements
    assert len(coll) == 2
    assert all(isinstance(x, Locator) for x in coll)


def test_nth_selector(fake_wrapper):
    loc = Locator(fake_wrapper, "els")
    nth = loc.nth(1)
    assert nth.index == 1


def test_first_and_last(fake_wrapper):
    loc = Locator(fake_wrapper, "els")
    first = loc.first()
    last = loc.last()
    assert first.index == 0
    assert last.index == loc.count() - 1


# ---------------------
#  Filtering
# ---------------------


def test_filter_has_text(fake_wrapper, fake_element):
    fake_element.text = "Match TEXT"
    loc = Locator(fake_wrapper, "els")
    results = loc.filter(has_text="Match")
    assert all("filtered" in x.description for x in results)


def test_filter_has_not_text(fake_wrapper, fake_element):
    fake_element.text = "Skip ME"
    loc = Locator(fake_wrapper, "els")
    results = loc.filter(has_not_text="Skip")
    assert not results


def test_filter_has_attribute(fake_wrapper, fake_element):
    loc = Locator(fake_wrapper, "els")
    fake_element.get_attribute.return_value = "val"
    results = loc.filter(has_attribute=("role", "val"))
    assert results


def test_filter_has_regex(fake_wrapper, fake_element):
    fake_element.text = "User 1234"
    loc = Locator(fake_wrapper, "els")
    results = loc.filter(has_regex=r"\d+")
    assert results


def test_filter_has_callable(fake_wrapper, fake_element):
    loc = Locator(fake_wrapper, "els")
    results = loc.filter(has=lambda el: True)
    assert results


def test_first_filtered_raises(fake_wrapper):
    loc = Locator(fake_wrapper, "els")
    with pytest.raises(AssertionError):
        loc.first_filtered(has_text="Nope")


def test_last_filtered(fake_wrapper, fake_element):
    fake_element.text = "Keeps"
    fake_wrapper.find_all.return_value = [fake_element]
    fake_wrapper.get_text.return_value = fake_element.text  # 👈 Fix here
    loc = Locator(fake_wrapper, "els")
    last = loc.last_filtered(has_text="Keeps")
    assert last.text == fake_element.text


# ---------------------
#  Dynamic getattr
# ---------------------


def test_getattr_delegates_to_element(fake_wrapper, fake_element):
    fake_wrapper._resolve.return_value = fake_element
    loc = Locator(fake_wrapper, "els")
    fake_element.custom_method = Mock(return_value=None)
    # getattr -> wrapper
    assert loc.custom_method() is loc
    fake_element.custom_value = "VALUE"
    assert loc.custom_value == "VALUE"


def test_xpath_child_startswith_dot_slash_slash(fake_wrapper):
    parent = Locator(fake_wrapper, "//div")
    child = Locator(fake_wrapper, ".//span", parent=parent)
    child.locator_type = LocatorType.XPATH
    result = child.full_selector
    assert result == "//div//span"  # .// removed


def test_xpath_child_startswith_dot_slash(fake_wrapper):
    parent = Locator(fake_wrapper, "//div")
    child = Locator(fake_wrapper, "./span", parent=parent)
    child.locator_type = LocatorType.XPATH
    result = child.full_selector
    assert result == "//div//span"  # ./ removed


def test_full_selector_default_css_descendant(fake_wrapper):
    parent = Locator(fake_wrapper, "div")
    child = Locator(fake_wrapper, "span", parent=parent)
    child.locator_type = LocatorType.CSS  # Not XPATH
    result = child.full_selector
    assert result == "div span"


def test_get_dom_attribute(fake_wrapper):
    fake_wrapper.get_dom_attribute.return_value = "data-value"
    loc = Locator(fake_wrapper, "button")
    result = loc.get_dom_attribute("data-test")
    assert result == "data-value"
    fake_wrapper.get_dom_attribute.assert_called_once_with(loc, "data-test")


def test_get_dom_property(fake_wrapper):
    fake_wrapper.get_dom_property.return_value = "DOM_PROP"
    loc = Locator(fake_wrapper, "input")
    result = loc.get_dom_property("aria-hidden")
    assert result == "DOM_PROP"
    fake_wrapper.get_dom_property.assert_called_once_with(loc, "aria-hidden")


def test_location_property(fake_wrapper):
    fake_wrapper.get_location.return_value = {"x": 100, "y": 200}
    loc = Locator(fake_wrapper, "div")
    result = loc.location
    assert result == {"x": 100, "y": 200}
    fake_wrapper.get_location.assert_called_once_with(loc)


def test_location_once_scrolled_into_view(fake_wrapper):
    fake_wrapper.get_location_scrolled.return_value = {"x": 50, "y": 75}
    loc = Locator(fake_wrapper, "div")
    result = loc.location_once_scrolled_into_view
    assert result == {"x": 50, "y": 75}
    fake_wrapper.get_location_scrolled.assert_called_once_with(loc)


def test_size_property(fake_wrapper):
    fake_wrapper.get_size.return_value = {"width": 300, "height": 150}
    loc = Locator(fake_wrapper, "img")
    result = loc.size
    assert result == {"width": 300, "height": 150}
    fake_wrapper.get_size.assert_called_once_with(loc)


def test_rect_property(fake_wrapper):
    fake_wrapper.get_rect.return_value = {"x": 10, "y": 20, "width": 100, "height": 50}
    loc = Locator(fake_wrapper, "canvas")
    result = loc.rect
    assert result == {"x": 10, "y": 20, "width": 100, "height": 50}
    fake_wrapper.get_rect.assert_called_once_with(loc)


def test_screenshot(fake_wrapper):
    fake_wrapper.screenshot.return_value = True
    loc = Locator(fake_wrapper, "section")
    result = loc.screenshot("screenshot.png")
    assert result is True
    fake_wrapper.screenshot.assert_called_once_with(loc, "screenshot.png")


def test_screenshot_as_png(fake_wrapper):
    fake_wrapper.screenshot_as_png.return_value = b"\x89PNG\r\n"
    loc = Locator(fake_wrapper, "section")
    result = loc.screenshot_as_png()
    assert result == b"\x89PNG\r\n"
    fake_wrapper.screenshot_as_png.assert_called_once_with(loc)


def test_screenshot_as_base64(fake_wrapper):
    fake_wrapper.screenshot_as_base64.return_value = "iVBORw0KGgoAAAANSUhEUgAAAAUA"
    loc = Locator(fake_wrapper, "canvas")
    result = loc.screenshot_as_base64()
    assert result == "iVBORw0KGgoAAAANSUhEUgAAAAUA"
    fake_wrapper.screenshot_as_base64.assert_called_once_with(loc)


def test_fill_calls_clear_and_send_keys(fake_wrapper):
    loc = Locator(fake_wrapper, "input")
    loc.clear = Mock(return_value=loc)
    loc.send_keys = Mock(return_value=loc)

    result = loc.fill("hello")

    loc.clear.assert_called_once()
    loc.send_keys.assert_called_once_with("hello")
    assert result is loc  # chaining result from _maybe_chain


def test_press_calls_send_keys_and_chains(fake_wrapper):
    loc = Locator(fake_wrapper, "input")
    loc.send_keys = Mock(return_value=loc)

    result = loc.press("Enter")

    loc.send_keys.assert_called_once_with("Enter")
    assert result is loc


def test_find_by_has(fake_wrapper):
    def resolve_locator_mock(selector):
        if selector == "div":
            return ("HAS", "something")
        return ("BY", selector)

    fake_wrapper.resolve_locator.side_effect = resolve_locator_mock
    fake_wrapper._find_by_has.return_value = "element"

    loc = Locator(fake_wrapper, "div")
    loc.index = None

    result = loc._find()

    assert result == "element"
    fake_wrapper._find_by_has.assert_called_once_with(loc)


def test_find_by_pseudo(fake_wrapper):
    # Explicitly match the input to full_selector
    def resolve_locator_mock(selector):
        if selector == "::before":
            return ("PSEUDO", "::before")
        return ("BY", selector)  # fallback

    fake_wrapper.resolve_locator.side_effect = resolve_locator_mock
    fake_wrapper._find_by_pseudo.return_value = "pseudo-element"

    loc = Locator(fake_wrapper, "::before")
    loc.index = None

    result = loc._find()

    assert result == "pseudo-element"
    fake_wrapper._find_by_pseudo.assert_called_once_with(loc)


def test_find_by_js_text(fake_wrapper):
    # Ensure resolve_locator returns JS_TEXT when full_selector is used
    def resolve_locator_mock(selector):
        if selector == "text=Click me":
            return ("JS_TEXT", "Click me")
        return ("BY", selector)

    fake_wrapper.resolve_locator.side_effect = resolve_locator_mock
    fake_wrapper.find_by_text.return_value = "text-element"

    loc = Locator(fake_wrapper, "text=Click me")
    loc.index = None

    result = loc._find()

    assert result == "text-element"
    fake_wrapper.find_by_text.assert_called_once_with("Click me")


def test_find_resolves_nth(fake_wrapper):
    fake_wrapper.resolve_locator.return_value = ("BY", "div")  # 👈 Match what Locator uses
    fake_wrapper._resolve_nth.return_value = "nth-element"

    loc = Locator(fake_wrapper, "div")
    loc.index = 2

    result = loc._find()

    assert result == "nth-element"
    fake_wrapper._resolve_nth.assert_called_once_with("BY", "div", 2)  # 👈 Match above


def test_should_be_disabled_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, "button")
    result = loc.should_be_disabled(timeout=10)

    fake_wrapper.should_be_disabled.assert_called_once_with(loc, 10)
    assert result is loc


def test_should_be_checked_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, "input[type=checkbox]")
    result = loc.should_be_checked(timeout=7)

    fake_wrapper.should_be_checked.assert_called_once_with(loc, 7)
    assert result is loc


def test_should_not_be_checked_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, "#terms")
    result = loc.should_not_be_checked(timeout=3)

    fake_wrapper.should_not_be_checked.assert_called_once_with(loc, 3)
    assert result is loc


def test_should_not_have_text_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, ".alert")
    result = loc.should_not_have_text("Error", timeout=4)

    fake_wrapper.should_not_have_text.assert_called_once_with(loc, "Error", 4)
    assert result is loc


def test_should_have_attribute_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, "a.link")
    result = loc.should_have_attribute("href", "https://example.com", timeout=6)

    fake_wrapper.should_have_attribute.assert_called_once_with(
        loc, "href", "https://example.com", 6
    )
    assert result is loc


def test_should_have_property_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, "input[type=text]")
    result = loc.should_have_property("value", "test123", timeout=8)

    fake_wrapper.should_have_property.assert_called_once_with(loc, "value", "test123", 8)
    assert result is loc


def test_should_have_value_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, "input#email")
    result = loc.should_have_value("user@example.com", timeout=2)

    fake_wrapper.should_have_value.assert_called_once_with(loc, "user@example.com", 2)
    assert result is loc


def test_should_have_css_calls_wrapper(fake_wrapper):
    loc = Locator(fake_wrapper, ".btn")
    result = loc.should_have_css("color", "rgb(255, 0, 0)", timeout=1)

    fake_wrapper.should_have_css.assert_called_once_with(loc, "color", "rgb(255, 0, 0)", 1)
    assert result is loc


def test_all_calls_find_all_shadow_for_shadow_locators(fake_wrapper):
    fake_wrapper._find_all_shadow.return_value = [Mock(), Mock()]
    loc = Locator(fake_wrapper, "div >>> span")  # 👉 triggers is_shadow = True
    loc.by = "CSS"
    loc.value = "div >>> span"

    result = loc.all()
    assert len(result) == 2
    fake_wrapper._find_all_shadow.assert_called_once_with(loc)


def test_all_calls_find_all_by_text(fake_wrapper):
    fake_wrapper._find_all_by_text.return_value = [Mock(), Mock()]
    loc = Locator(fake_wrapper, "text=Login")
    loc.by = "TEXT"
    loc.value = "Login"

    result = loc.all()
    assert len(result) == 2
    fake_wrapper._find_all_by_text.assert_called_once_with(loc)


def test_all_calls_find_all_by_has_text(fake_wrapper):
    fake_wrapper._find_all_by_has_text.return_value = [Mock(), Mock()]
    loc = Locator(fake_wrapper, "div")
    loc.by = "HAS_TEXT"
    loc.value = "div"

    result = loc.all()
    assert len(result) == 2
    fake_wrapper._find_all_by_has_text.assert_called_once_with(loc)


def test_all_calls_find_all_by_has(fake_wrapper):
    fake_wrapper._find_all_by_has.return_value = [Mock(), Mock()]
    loc = Locator(fake_wrapper, "div")
    loc.by = "HAS"
    loc.value = "div"

    result = loc.all()
    assert len(result) == 2
    fake_wrapper._find_all_by_has.assert_called_once_with(loc)


def test_all_calls_find_all_by_pseudo(fake_wrapper):
    fake_wrapper._find_all_by_pseudo.return_value = [Mock(), Mock()]
    loc = Locator(fake_wrapper, "::before")
    loc.by = "PSEUDO"
    loc.value = "::before"

    result = loc.all()
    assert len(result) == 2
    fake_wrapper._find_all_by_pseudo.assert_called_once_with(loc)


def test_filter_has_attribute_matches(fake_wrapper, fake_element):
    fake_element.get_attribute.return_value = "btn"
    fake_wrapper.find_all.return_value = [fake_element]

    loc = Locator(fake_wrapper, "button")
    results = loc.filter(has_attribute=("role", "btn"))

    assert len(results) == 1
    assert results[0].index == 0
    fake_element.get_attribute.assert_called_with("role")


def test_filter_with_regex_match(fake_wrapper, fake_element):
    fake_element.text = "User 12345"
    fake_wrapper.find_all.return_value = [fake_element]

    loc = Locator(fake_wrapper, "div")
    results = loc.filter(has_regex=r"User \d+")

    assert len(results) == 1
    assert results[0].index == 0


def test_filter_with_regex_no_match(fake_wrapper, fake_element):
    fake_element.text = "Admin"
    fake_wrapper.find_all.return_value = [fake_element]

    loc = Locator(fake_wrapper, "div")
    results = loc.filter(has_regex=r"User \d+")

    assert len(results) == 0


def test_filter_with_has_callable_passes(fake_wrapper, fake_element):
    fake_element.text = "OK"
    fake_wrapper.find_all.return_value = [fake_element]

    loc = Locator(fake_wrapper, "span")
    results = loc.filter(has=lambda el: el.text == "OK")

    assert len(results) == 1
    assert results[0].index == 0


def test_filter_with_has_callable_fails(fake_wrapper, fake_element):
    fake_element.text = "NOPE"
    fake_wrapper.find_all.return_value = [fake_element]

    loc = Locator(fake_wrapper, "span")
    results = loc.filter(has=lambda el: el.text == "OK")

    assert results == []


def test_first_filtered_returns_first_match(fake_wrapper, fake_element):
    fake_element.text = "MatchMe"
    fake_wrapper.find_all.return_value = [fake_element]

    loc = Locator(fake_wrapper, "div")
    result = loc.first_filtered(has_text="MatchMe")

    assert isinstance(result, Locator)
    assert result.index == 0


def test_last_returns_last_element(fake_wrapper):
    fake_wrapper.find_all.return_value = [Mock(), Mock(), Mock()]  # count = 3

    loc = Locator(fake_wrapper, ".item")
    result = loc.last()

    assert isinstance(result, Locator)
    assert result.index == 2
    fake_wrapper.resolve_locator.assert_called_with(result.full_selector)


def test_find_by_has_text(fake_wrapper):
    def resolve_locator_mock(selector):
        if selector == "div":  # 👈 This must match `loc.full_selector`
            return ("HAS_TEXT", "something")
        return ("BY", selector)

    fake_wrapper.resolve_locator.side_effect = resolve_locator_mock
    fake_wrapper._find_by_has_text.return_value = "element"

    loc = Locator(fake_wrapper, "div")
    loc.index = None  # avoid nth path

    result = loc._find()

    assert result == "element"
    fake_wrapper._find_by_has_text.assert_called_once_with(loc)
