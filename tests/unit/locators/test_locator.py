from unittest.mock import MagicMock

import pytest

from nrobo.locators.locator import Locator
from nrobo.locators.locator_collection import LocatorCollection


# ---------------------------------
# Reusable fixture
# ---------------------------------
@pytest.fixture
def wrapper():
    w = MagicMock()
    w.resolve_locator.return_value = ("css", "div")
    return w


@pytest.fixture
def locator(wrapper):
    return Locator(wrapper, "#btn")


class DummyWrapper:
    """Wrapper stub implementing find_all + resolve_locator for tests."""

    def __init__(self, elements):
        self.elements = elements

    # default case
    def find_all(self, locator):
        return self.elements

    # branch cases
    def _find_all_shadow(self, locator):
        return self.elements

    def _find_all_by_text(self, locator):
        return self.elements

    def _find_all_by_has_text(self, locator):
        return self.elements

    def _find_all_by_has(self, locator):
        return self.elements

    def _find_all_by_pseudo(self, locator):
        return self.elements

    # required for Locator.__init__
    def resolve_locator(self, locator):
        return "CSS", locator


class DummyElement:
    """Simple fake element with text + attributes."""

    def __init__(self, text="", attrs=None):
        self.text = text
        self._attrs = attrs or {}

    def get_attribute(self, name):
        return self._attrs.get(name)


def make_locator(elements):
    wrapper = DummyWrapper(elements)
    loc = Locator(wrapper, "div", "div")
    loc.by = "CSS"
    loc.value = "div"
    return loc


class FakeEl:
    def __init__(self, text="hello", attrs=None):
        self.text = text
        self.attrs = attrs or {}
        self.tag_name = "div"

    def get_attribute(self, name):
        return self.attrs.get(name)

    def click(self):
        return None

    def clear(self):
        return None

    def send_keys(self, *keys):
        return None


class FakeWrapper:
    def __init__(self):
        self.calls = []

    def resolve_locator(self, locator):
        return ("CSS", locator)

    def click(self, loc):
        self.calls.append(("click", loc))

    def clear(self, loc):
        self.calls.append(("clear", loc))

    def send_keys(self, loc, *keys):
        self.calls.append(("send_keys", loc, keys))

    def submit(self, loc):
        self.calls.append(("submit", loc))

    def is_displayed(self, loc):
        return True

    def get_text(self, loc):
        return "TEXT"

    def get_tag_name(self, loc):
        return "span"

    def get_attribute(self, loc, name):
        return f"attr-{name}"

    def get_property(self, loc, name):
        return f"prop-{name}"

    def get_dom_attribute(self, loc, name):
        return f"domattr-{name}"

    def get_dom_property(self, loc, name):
        return f"domprop-{name}"

    def value_of_css_property(self, loc, prop):
        return f"css-{prop}"

    def get_location(self, loc):
        return {"x": 1}

    def get_location_scrolled(self, loc):
        return {"x": 2}

    def get_size(self, loc):
        return {"w": 10}

    def get_rect(self, loc):
        return {"h": 20}

    # Element fetchers
    def _resolve(self, loc):
        return FakeEl("one")

    def _resolve_nth(self, loc, n):
        return FakeEl(f"nth-{n}")

    def _find_shadow(self, loc):
        return FakeEl("shadow")

    def _find_by_text(self, loc):
        return FakeEl("text")

    def _find_by_has_text(self, loc):
        return FakeEl("has-text")

    def _find_by_has(self, loc):
        return FakeEl("has")

    def _find_by_pseudo(self, loc):
        return FakeEl("pseudo")

    def _find_all_shadow(self, loc):
        return [FakeEl("s1"), FakeEl("s2")]

    def _find_all_by_text(self, loc):
        return [FakeEl("t1"), FakeEl("t2")]

    def _find_all_by_has_text(self, loc):
        return [FakeEl("ht1"), FakeEl("ht2")]

    def _find_all_by_has(self, loc):
        return [FakeEl("h1"), FakeEl("h2")]

    def _find_all_by_pseudo(self, loc):
        return [FakeEl("p1"), FakeEl("p2")]

    def find_all(self, loc):
        return [FakeEl("a"), FakeEl("b"), FakeEl("c")]


def test_locator_init_resolves_locator():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, "#id")

    assert loc.by == "CSS"
    assert loc.value == "#id"
    assert loc.description == "#id"


def test_locator_actions_call_wrapper():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, "#id")

    loc.click()
    loc.clear()
    loc.send_keys("x", "y")

    assert wrapper.calls == [
        ("click", loc),
        ("clear", loc),
        ("send_keys", loc, ("x", "y")),
    ]


def test_locator_properties():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, "#id")

    assert loc.text == "TEXT"
    assert loc.tag_name == "span"
    assert loc.location == {"x": 1}
    assert loc.location_once_scrolled_into_view == {"x": 2}
    assert loc.size == {"w": 10}
    assert loc.rect == {"h": 20}


def test_find_shadow_1():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, "shadow::#a")
    assert loc._find().text == "shadow"


def test_nth_first_last():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, ".item")

    assert loc.nth(1).index == 1
    assert loc.first().index == 0
    assert loc.last().index == 2  # 3 elements from find_all


def test_all_returns_collection():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, ".x")

    result = loc.all()
    assert isinstance(result, LocatorCollection)
    assert len(result) == 3
    assert result[0].index == 0
    assert result[1].index == 1


def test_filter_has_text():
    wrapper = FakeWrapper()
    wrapper.find_all = lambda loc: [FakeEl("Login"), FakeEl("Hello")]

    loc = Locator(wrapper, ".x")
    res = loc.filter(has_text="Login")

    assert len(res) == 1
    assert isinstance(res[0], Locator)


def test_filter_has_attribute():
    wrapper = FakeWrapper()
    wrapper.find_all = lambda loc: [FakeEl("", {"role": "button"}), FakeEl("", {"role": "input"})]

    loc = Locator(wrapper, ".x")
    res = loc.filter(has_attribute=("role", "button"))

    assert len(res) == 1


def test_filter_has_regex():
    wrapper = FakeWrapper()
    wrapper.find_all = lambda loc: [FakeEl("User 12"), FakeEl("ABC")]

    loc = Locator(wrapper, ".x")
    res = loc.filter(has_regex=r"User \d+")

    assert len(res) == 1
    assert isinstance(res[0], Locator)


def test_first_filtered_raises():
    wrapper = FakeWrapper()
    wrapper.find_all = lambda loc: []

    loc = Locator(wrapper, ".x")

    with pytest.raises(AssertionError):
        loc.first_filtered(has_text="Login")


def test_getattr_wraps_webelement_methods():
    wrapper = FakeWrapper()
    el = FakeEl()
    wrapper._resolve = lambda loc: el

    loc = Locator(wrapper, ".x")

    # FakeEl.click returns None -> wrapper should return locator itself
    assert loc.click() is loc


# -------------------------------
# TEST: Initialization
# -------------------------------
def test_locator_initialization(wrapper):
    loc = Locator(wrapper, "#btn", "Button")
    assert loc.selector == "#btn"
    assert loc.description == "Button"
    assert loc.by == "css"
    assert loc.value == "div"
    assert loc.index is None
    assert loc.is_shadow is False


# -------------------------------
# TEST: click/clear/send_keys call wrapper methods
# -------------------------------
def test_click_calls_wrapper(wrapper):
    loc = Locator(wrapper, "#btn")
    loc.click()
    wrapper.click.assert_called_once_with(loc)


def test_clear_calls_wrapper(wrapper):
    loc = Locator(wrapper, "#inp")
    loc.clear()
    wrapper.clear.assert_called_once_with(loc)


def test_send_keys_calls_wrapper(wrapper):
    loc = Locator(wrapper, "#inp")
    loc.send_keys("abc", 123)
    wrapper.send_keys.assert_called_once_with(loc, "abc", 123)


# -------------------------------
# TEST: __getattr__ fallback to WebElement
# -------------------------------
def test_getattr_forwards_to_webelement(wrapper):
    mock_el = MagicMock()
    wrapper._resolve.return_value = mock_el

    loc = Locator(wrapper, "#x")
    loc.some_method("hello")

    mock_el.some_method.assert_called_once_with("hello")


def test_getattr_chainable_when_method_returns_none(wrapper):
    mock_el = MagicMock()
    mock_el.do_something.return_value = None
    wrapper._resolve.return_value = mock_el

    loc = Locator(wrapper, "#x")
    result = loc.do_something()

    assert result is loc  # chainable


# -------------------------------
# TEST: nth() creates new locator
# -------------------------------
def test_nth_creates_new_locator(wrapper):
    loc = Locator(wrapper, ".item")
    loc2 = loc.nth(3)

    assert isinstance(loc2, Locator)
    assert loc2.index == 3
    assert loc2.selector == ".item"


# -------------------------------
# TEST: all() returns LocatorCollection
# -------------------------------
def test_all_returns_locator_collection(wrapper):
    wrapper.find_all.return_value = ["el1", "el2", "el3"]

    loc = Locator(wrapper, ".item")
    collection = loc.all()

    assert isinstance(collection, LocatorCollection)
    assert len(collection) == 3
    assert collection[0].index == 0
    assert collection[1].index == 1
    assert collection[2].index == 2


# -------------------------------
# TEST: last() helper
# -------------------------------
def test_last_returns_last_locator(wrapper):
    wrapper.find_all.return_value = ["a", "b", "c"]

    loc = Locator(wrapper, ".item")
    last_loc = loc.last()

    assert last_loc.index == 2


def test_last_raises_if_empty(wrapper):
    wrapper.find_all.return_value = []

    loc = Locator(wrapper, ".item")

    with pytest.raises(AssertionError):
        loc.last()


# -------------------------------
# TEST: count()
# -------------------------------
def test_count(wrapper):
    wrapper.find_all.return_value = ["a", "b", "c", "d"]
    loc = Locator(wrapper, ".item")
    assert loc.count() == 4


# -------------------------------
# TEST: filter()
# -------------------------------
def test_filter_by_text(wrapper):
    el1 = MagicMock()
    el1.text = "Login now"
    el2 = MagicMock()
    el2.text = "Hello"
    el3 = MagicMock()
    el3.text = "Login successful"

    wrapper.find_all.return_value = [el1, el2, el3]

    loc = Locator(wrapper, ".item")
    results = loc.filter(has_text="Login")

    assert len(results) == 2
    assert results[0].index == 0
    assert results[1].index == 2


def test_filter_by_attribute(wrapper):
    el1 = MagicMock()
    el1.text = ""
    el1.get_attribute.return_value = "button"
    el2 = MagicMock()
    el2.text = ""
    el2.get_attribute.return_value = "link"

    wrapper.find_all.return_value = [el1, el2]

    loc = Locator(wrapper, ".item")
    results = loc.filter(has_attribute=("role", "button"))

    assert len(results) == 1
    assert results[0].index == 0


def test_filter_by_regex(wrapper):
    el1 = MagicMock()
    el1.text = "User 42"
    el2 = MagicMock()
    el2.text = "Admin"
    wrapper.find_all.return_value = [el1, el2]

    loc = Locator(wrapper, ".item")
    results = loc.filter(has_regex=r"User \d+")

    assert len(results) == 1
    assert results[0].index == 0


# -------------------------------
# TEST: first_filtered / last_filtered
# -------------------------------
def test_first_filtered(wrapper):
    el1 = MagicMock()
    el1.text = "A"
    el2 = MagicMock()
    el2.text = "Login"
    wrapper.find_all.return_value = [el1, el2]

    loc = Locator(wrapper, ".item")
    first = loc.first_filtered(has_text="Login")

    assert first.index == 1


def test_first_filtered_no_match(wrapper):
    wrapper.find_all.return_value = []

    loc = Locator(wrapper, ".item")
    with pytest.raises(AssertionError):
        loc.first_filtered(has_text="X")


def test_last_filtered(wrapper):
    el1 = MagicMock()
    el1.text = "Login"
    el2 = MagicMock()
    el2.text = "Hello Login"
    wrapper.find_all.return_value = [el1, el2]

    loc = Locator(wrapper, ".item")
    last = loc.last_filtered(has_text="Login")

    assert last.index == 1


# -------------------------------
# TEST: _find() dispatch logic
# -------------------------------
def test_find_shadow_2(wrapper):
    loc = Locator(wrapper, "div >>> span")
    loc.is_shadow = True
    loc._find()
    wrapper._find_shadow.assert_called_once_with(loc)


def test_find_text(wrapper):
    loc = Locator(wrapper, "text=Login")
    loc.by = "TEXT"
    loc._find()
    wrapper._find_by_text.assert_called_once_with(loc)


def test_find_has_text(wrapper):
    loc = Locator(wrapper, "button:has-text('X')")
    loc.by = "HAS_TEXT"
    loc._find()
    wrapper._find_by_has_text.assert_called_once_with(loc)


def test_find_pseudo(wrapper):
    loc = Locator(wrapper, "button:visible")
    loc.by = "PSEUDO"
    loc._find()
    wrapper._find_by_pseudo.assert_called_once_with(loc)


def test_find_single(wrapper):
    loc = Locator(wrapper, ".item")
    loc.by = "css"
    loc.index = None
    loc._find()
    wrapper._resolve.assert_called_once_with(loc)


def test_find_nth(wrapper):
    loc = Locator(wrapper, ".item")
    loc.by = "css"
    loc.index = 3
    loc._find()
    wrapper._resolve_nth.assert_called_once_with(loc, 3)


def test_get_property(locator, wrapper):
    wrapper.get_property.return_value = "ABC"

    value = locator.get_property("name")

    wrapper.get_property.assert_called_once_with(locator, "name")
    assert value == "ABC"


def test_get_dom_attribute(locator, wrapper):
    wrapper.get_dom_attribute.return_value = "xyz"

    value = locator.get_dom_attribute("role")

    wrapper.get_dom_attribute.assert_called_once_with(locator, "role")
    assert value == "xyz"


def test_get_dom_property(locator, wrapper):
    wrapper.get_dom_property.return_value = "OK"

    value = locator.get_dom_property("checked")

    wrapper.get_dom_property.assert_called_once_with(locator, "checked")
    assert value == "OK"


def test_value_of_css_property(locator, wrapper):
    wrapper.value_of_css_property.return_value = "10px"

    val = locator.value_of_css_property("margin")

    wrapper.value_of_css_property.assert_called_once_with(locator, "margin")
    assert val == "10px"


def test_location_property(locator, wrapper):
    wrapper.get_location.return_value = {"x": 10, "y": 20}

    assert locator.location == {"x": 10, "y": 20}
    wrapper.get_location.assert_called_once_with(locator)


def test_location_scrolled_property(locator, wrapper):
    wrapper.get_location_scrolled.return_value = {"x": 5, "y": 100}

    assert locator.location_once_scrolled_into_view == {"x": 5, "y": 100}
    wrapper.get_location_scrolled.assert_called_once_with(locator)


def test_size_property(locator, wrapper):
    wrapper.get_size.return_value = {"w": 200, "h": 50}

    assert locator.size == {"w": 200, "h": 50}
    wrapper.get_size.assert_called_once_with(locator)


def test_rect_property(locator, wrapper):
    wrapper.get_rect.return_value = {"x": 0, "y": 0, "width": 100, "height": 40}

    assert locator.rect == {"x": 0, "y": 0, "width": 100, "height": 40}
    wrapper.get_rect.assert_called_once_with(locator)


def test_screenshot_calls_wrapper(locator, wrapper):
    wrapper.screenshot.return_value = True

    result = locator.screenshot("file.png")

    wrapper.screenshot.assert_called_once_with(locator, "file.png")
    assert result is True


def test_screenshot_as_png(locator, wrapper):
    wrapper.screenshot_as_png.return_value = b"BINARYDATA"

    assert locator.screenshot_as_png() == b"BINARYDATA"
    wrapper.screenshot_as_png.assert_called_once_with(locator)


def test_screenshot_as_base64(locator, wrapper):
    wrapper.screenshot_as_base64.return_value = "base64data=="

    assert locator.screenshot_as_base64() == "base64data=="
    wrapper.screenshot_as_base64.assert_called_once_with(locator)


def test_fill_calls_clear_and_send_keys(locator, wrapper):
    locator.fill("hello")

    wrapper.clear.assert_called_once_with(locator)
    wrapper.send_keys.assert_called_once_with(locator, "hello")


def test_press_calls_send_keys(locator, wrapper):
    locator.press("ENTER")

    wrapper.send_keys.assert_called_once_with(locator, "ENTER")


def test_getattr_forwards_method_and_returns_result(wrapper):
    mock_el = MagicMock()
    mock_el.some_method.return_value = "RESULT"

    wrapper._resolve.return_value = mock_el

    loc = Locator(wrapper, "#x")
    assert loc.some_method(1, 2) == "RESULT"
    mock_el.some_method.assert_called_once_with(1, 2)


def test_getattr_chainable_when_method_returns_none_(wrapper):
    mock_el = MagicMock()
    mock_el.some_method.return_value = None

    wrapper._resolve.return_value = mock_el

    loc = Locator(wrapper, "#x")
    result = loc.some_method()

    assert result is loc
    mock_el.some_method.assert_called_once()


def test_find_shadow_3(wrapper):
    loc = Locator(wrapper, "#x")
    loc.is_shadow = True

    loc._find()
    wrapper._find_shadow.assert_called_once_with(loc)


def test_find_text_branch(wrapper):
    loc = Locator(wrapper, "#x")
    loc.by = "TEXT"

    loc._find()
    wrapper._find_by_text.assert_called_once_with(loc)


def test_find_has_text_branch(wrapper):
    loc = Locator(wrapper, "#x")
    loc.by = "HAS_TEXT"

    loc._find()
    wrapper._find_by_has_text.assert_called_once_with(loc)


def test_find_has_branch(wrapper):
    loc = Locator(wrapper, "#x")
    loc.by = "HAS"

    loc._find()
    wrapper._find_by_has.assert_called_once_with(loc)


def test_find_pseudo_branch(wrapper):
    loc = Locator(wrapper, "#x")
    loc.by = "PSEUDO"

    loc._find()
    wrapper._find_by_pseudo.assert_called_once_with(loc)


def test_find_default_branch(wrapper):
    loc = Locator(wrapper, "#x")
    loc.by = "css"
    loc.index = None

    loc._find()
    wrapper._resolve.assert_called_once_with(loc)


def test_find_nth_branch(wrapper):
    loc = Locator(wrapper, "#x")
    loc.by = "css"
    loc.index = 3

    loc._find()
    wrapper._resolve_nth.assert_called_once_with(loc, 3)


@pytest.mark.parametrize(
    "method_name, wrapper_method, args",
    [
        ("should_be_visible", "should_be_visible", (5,)),
        ("should_have_text", "should_have_text", ("X", 5)),
        ("should_be_enabled", "should_be_enabled", (5,)),
        ("should_be_disabled", "should_be_disabled", (5,)),
        ("should_contain_text", "should_contain_text", ("X", 5)),
        ("should_not_be_visible", "should_not_be_visible", (5,)),
        ("should_be_checked", "should_be_checked", (5,)),
        ("should_not_be_checked", "should_not_be_checked", (5,)),
        ("should_not_have_text", "should_not_have_text", ("X", 5)),
        ("should_have_exact_text", "should_have_exact_text", ("X", 5)),
        # SPECIAL CASES → need (name, expected)
        ("should_have_attribute", "should_have_attribute", ("name", "value", 5)),
        ("should_have_property", "should_have_property", ("prop", "value", 5)),
        ("should_have_value", "should_have_value", ("X", 5)),
        ("should_have_css", "should_have_css", ("color", "red", 5)),
        ("should_match_regex", "should_match_regex", ("^abc$", 5)),
    ],
)
def test_should_methods(locator, wrapper, method_name, wrapper_method, args):
    method = getattr(locator, method_name)

    # --- call with expected args
    result = method(*args)

    # verify wrapper call forwarded correctly
    wrapper_call = getattr(wrapper, wrapper_method)
    wrapper_call.assert_called_once()

    # chainable?
    assert result is locator


def test_filter_handles_text_exception():
    bad_el = MagicMock()
    type(bad_el).text = property(lambda self: (_ for _ in ()).throw(Exception("boom")))

    loc = make_locator([bad_el])

    result = loc.filter(has_text="anything")

    assert result == []


def test_filter_excludes_has_not_text():
    el1 = DummyElement("Error: something wrong")
    el2 = DummyElement("All good")

    loc = make_locator([el1, el2])

    result = loc.filter(has_not_text="Error")

    # el1 excluded, el2 included
    assert len(result) == 1
    assert result[0].index == 1  # second element only


def test_filter_custom_has_predicate():
    el1 = DummyElement("Hello")
    el2 = DummyElement("World")
    loc = make_locator([el1, el2])

    # Keep only elements whose text == "World"
    result = loc.filter(has=lambda el: el.text == "World")

    assert len(result) == 1
    assert result[0].index == 1  # element 2 kept


def test_filter_creates_locator_on_match():
    el1 = DummyElement("Login page")
    el2 = DummyElement("Dashboard")

    loc = make_locator([el1, el2])

    result = loc.filter(has_text="Login")

    assert len(result) == 1
    new_loc = result[0]

    assert new_loc.index == 0
    assert new_loc.selector == "div"
    assert "filtered:0" in new_loc.description


def test_all_shadow_branch():
    wrapper = DummyWrapper(["e1", "e2"])
    loc = Locator(wrapper, "div >>> span")  # triggers is_shadow=True
    loc.is_shadow = True  # enforce branch
    loc.by = "CSS"

    collection = loc.all()

    assert len(collection) == 2
    assert collection[0].index == 0
    assert collection[1].index == 1


def test_all_text_branch():
    wrapper = DummyWrapper(["e1", "e2"])
    loc = Locator(wrapper, "text=Login")
    loc.by = "TEXT"

    collection = loc.all()

    assert len(collection) == 2
    assert collection[0].index == 0
    assert collection[1].index == 1


def test_all_has_text_branch():
    wrapper = DummyWrapper(["e1", "e2", "e3"])
    loc = Locator(wrapper, "x")
    loc.by = "HAS_TEXT"

    collection = loc.all()

    assert len(collection) == 3
    assert collection[2].index == 2


def test_all_has_branch():
    wrapper = DummyWrapper(["a", "b"])
    loc = Locator(wrapper, "div")
    loc.by = "HAS"

    collection = loc.all()

    assert len(collection) == 2
    assert collection[1].index == 1


def test_all_pseudo_branch():
    wrapper = DummyWrapper(["el"])
    loc = Locator(wrapper, "button:visible")
    loc.by = "PSEUDO"

    collection = loc.all()

    assert len(collection) == 1
    assert collection[0].index == 0


def test_all_default_branch():
    wrapper = DummyWrapper(["x1", "x2", "x3"])
    loc = Locator(wrapper, "#id")
    loc.by = "CSS"  # anything that does not hit earlier branches

    collection = loc.all()

    assert len(collection) == 3
    assert collection[0].description.endswith("[0]")
    assert collection[2].index == 2


def test_all_returns_locator_collection_():
    wrapper = DummyWrapper(["X"])
    loc = Locator(wrapper, ".cls")

    result = loc.all()

    assert isinstance(result, LocatorCollection)


def test_get_attribute_calls_wrapper_and_returns_value():
    wrapper = MagicMock()
    wrapper.resolve_locator.return_value = ("CSS", "#x")

    wrapper.get_attribute.return_value = "hello"

    loc = Locator(wrapper, "#x")

    result = loc.get_attribute("role")

    wrapper.get_attribute.assert_called_once_with(loc, "role")
    assert result == "hello"


def test_submit_calls_wrapper_and_is_chainable():
    wrapper = MagicMock()
    wrapper.resolve_locator.return_value = ("CSS", "form")

    loc = Locator(wrapper, "form")

    returned = loc.submit()

    wrapper.submit.assert_called_once_with(loc)
    assert returned is loc  # chainable


def test_find_calls_find_by_text_for_js_text_branch():
    """
    Ensure that when Locator.by == 'JS_TEXT', _find() calls wrapper.find_by_text(self.value).
    """

    # Mock SeleniumWrapper-like object
    mock_wrapper = MagicMock()
    mock_wrapper.resolve_locator.return_value = ("JS_TEXT", "example text")

    # Create Locator instance
    locator = Locator(wrapper=mock_wrapper, locator="dummy_locator", description="Dummy")

    # Manually confirm state
    assert locator.by == "JS_TEXT"
    assert locator.value == "example text"

    # Mock the wrapper.find_by_text return value
    expected_element = MagicMock(name="mock_element")
    mock_wrapper.find_by_text.return_value = expected_element

    # Call _find(), which should trigger the JS_TEXT branch
    result = locator._find()

    # Verify correct delegation and return value
    mock_wrapper.find_by_text.assert_called_once_with("example text")
    assert result is expected_element
