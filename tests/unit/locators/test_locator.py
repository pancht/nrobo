import pytest

from nrobo.locators.locator import Locator
from nrobo.locators.locator_collection import LocatorCollection


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


def test_find_shadow():
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
