import pytest

from nrobo.locators.locator import Locator
from nrobo.locators.locator_classifier import LocatorType


# -------------------------------------------------------------
# Fake WebElement + Wrapper for fully isolated unit tests
# -------------------------------------------------------------
class FakeEl:
    def __init__(self, text="TXT", attrs=None):
        self.text = text
        self.attrs = attrs or {}

    def click(self):
        return None

    def clear(self):
        return None

    def send_keys(self, *args):
        return None

    def get_attribute(self, name):
        return self.attrs.get(name)

    def get_property(self, name):
        return self.attrs.get(name)

    def get_dom_attribute(self, name):
        return self.attrs.get(name)

    def get_dom_property(self, name):
        return self.attrs.get(name)


class FakeWrapper:
    """
    A minimal fake wrapper that supports ALL code paths in Locator.
    Every call returns controlled values so the Locator can be fully tested.
    """

    def __init__(self):
        self.calls = []

    # ---------- Selector Resolution ----------
    def resolve_locator(self, selector):
        if selector.startswith("//"):
            return "XPATH", selector
        if selector.startswith("text="):
            return "TEXT", selector[5:]
        if selector.startswith(":"):
            return "PSEUDO", selector
        if ">>>" in selector:
            return "SHADOW", selector
        return "CSS", selector

    # ---------- Core resolution ----------
    def _resolve(self, locator):
        self.calls.append(("_resolve", locator.full_selector))
        return FakeEl()

    def _resolve_with(self, by, value):
        self.calls.append(("_resolve_with", by, value))
        return FakeEl()

    def _resolve_nth(self, by, value, index):
        self.calls.append(("_resolve_nth", by, value, index))
        return FakeEl(text=f"nth-{index}")

    # ---------- Text / pseudo / shadow search paths ----------
    def _find_by_text(self, locator):
        return FakeEl(text="TEXT_MATCH")

    def _find_by_has_text(self, locator):
        return FakeEl(text="HAS_TEXT_MATCH")

    def _find_by_has(self, locator):
        return FakeEl(text="HAS_MATCH")

    def _find_by_pseudo(self, locator):
        return FakeEl(text="PSEUDO_MATCH")

    def _find_shadow(self, locator):
        return FakeEl(text="SHADOW_MATCH")

    def find_by_text(self, value):
        return FakeEl(text=f"JS_TEXT:{value}")

    # ---------- All() paths ----------
    def _find_all_shadow(self, locator):
        return [FakeEl(), FakeEl()]

    def _find_all_by_text(self, locator):
        return [FakeEl("A"), FakeEl("B")]

    def _find_all_by_has_text(self, locator):
        return [FakeEl("X"), FakeEl("Y")]

    def _find_all_by_has(self, locator):
        return [FakeEl("X"), FakeEl("Y")]

    def _find_all_by_pseudo(self, locator):
        return [FakeEl(), FakeEl()]

    def find_all(self, locator):
        return [FakeEl("A"), FakeEl("B"), FakeEl("C")]

    # ---------- Assertion-like API ----------
    def should_be_visible(self, locator, timeout):
        self.calls.append(("visible", locator.full_selector, timeout))

    def should_have_text(self, locator, expected, timeout):
        self.calls.append(("has_text", expected))

    def should_have_attribute(self, locator, name, expected, timeout):
        self.calls.append(("attr", name, expected))

    def should_have_property(self, locator, name, expected, timeout):
        self.calls.append(("prop", name, expected))

    def should_have_value(self, locator, expected, timeout):
        self.calls.append(("value", expected))

    def should_have_css(self, locator, prop, expected, timeout):
        self.calls.append(("css", prop, expected))


# -------------------------------------------------------------
# 1. Constructor + attributes
# -------------------------------------------------------------
def test_locator_init_basic():
    wrapper = FakeWrapper()
    loc = Locator(wrapper, "#id")

    assert loc.selector == "#id"
    assert loc.locator_type == LocatorType.CSS
    assert loc.description == "#id"
    assert loc.parent is None


# -------------------------------------------------------------
# 2. full_selector chaining (ALL branches)
# -------------------------------------------------------------
def test_full_selector_xpath_relative():
    w = FakeWrapper()
    p = Locator(w, "//div")
    c = Locator(w, "./span", parent=p)
    assert c.full_selector == "//div//span"


def test_full_selector_xpath_absolute():
    w = FakeWrapper()
    p = Locator(w, "//div")
    c = Locator(w, "//span", parent=p)
    assert c.full_selector == "//span"


def test_full_selector_shadow():
    w = FakeWrapper()
    p = Locator(w, "div >>> span")
    c = Locator(w, "button", parent=p)
    assert c.full_selector == "div >>> span >>> button"


def test_full_selector_pseudo():
    w = FakeWrapper()
    p = Locator(w, "div")
    c = Locator(w, ":visible", parent=p)
    assert c.full_selector == "div:visible"


def test_full_selector_combinator():
    w = FakeWrapper()
    p = Locator(w, "ul")
    c = Locator(w, "> li", parent=p)
    assert c.full_selector == "ul> li"


def test_full_selector_default_css_descendant():
    w = FakeWrapper()
    p = Locator(w, "ul")
    c = Locator(w, "li", parent=p)
    assert c.full_selector == "ul li"


# -------------------------------------------------------------
# 3. locator() playwright-style chaining
# -------------------------------------------------------------
def test_locator_chaining_creates_new_instance():
    w = FakeWrapper()
    loc1 = Locator(w, "div")
    loc2 = loc1.locator("span")

    assert loc2.selector == "span"
    assert loc2.description.endswith("span")
    assert loc2.parent is None  # your current implementation


# -------------------------------------------------------------
# 4. Explicit API method delegation
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "method,args",
    [
        ("click", []),
        ("clear", []),
        ("send_keys", ["A"]),
        ("submit", []),
    ],
)
def test_explicit_methods_call_wrapper(method, args):
    w = FakeWrapper()
    loc = Locator(w, "div")

    # Patch wrapper method to track calls
    setattr(w, method, lambda self=None, l=None, *a: w.calls.append((method, a)))  # noqa: E741

    getattr(loc, method)(*args)
    assert w.calls, f"{method} not called"


# -------------------------------------------------------------
# 5. __getattr__ fallback
# -------------------------------------------------------------
def test_getattr_delegates_to_resolved_element():
    class E(FakeEl):
        def mymethod(self):
            return "OK"

    class W(FakeWrapper):
        def _resolve(self, locator):
            return E()

    w = W()
    loc = Locator(w, "div")

    assert loc.mymethod() == "OK"  # delegated call


# -------------------------------------------------------------
# 6. _find() dispatching paths
# -------------------------------------------------------------
@pytest.mark.parametrize(
    "selector,expected",
    [
        ("text=Login", "TEXT_MATCH"),
        (":visible", "PSEUDO_MATCH"),
        ("shadow::span", "SHADOW_MATCH"),
    ],
)
def test_find_dispatches(selector, expected):
    w = FakeWrapper()
    loc = Locator(w, selector)
    result = loc._find()
    assert result.text == expected


def test_find_nth_calls_nth_dispatch():
    w = FakeWrapper()
    loc = Locator(w, "div")
    loc.index = 2
    result = loc._find()
    assert result.text == "nth-2"


def test_find_default_calls_resolve_with():
    w = FakeWrapper()
    loc = Locator(w, "div")
    result = loc._find()
    assert isinstance(result, FakeEl)


# -------------------------------------------------------------
# 7. all() expansion
# -------------------------------------------------------------
def test_all_generates_locator_collection():
    w = FakeWrapper()
    loc = Locator(w, "div")
    coll = loc.all()

    assert len(coll) == 3
    assert coll[0].index == 0
    assert coll[1].index == 1


# -------------------------------------------------------------
# 8. filter() logic
# -------------------------------------------------------------
def test_filter_by_text():
    w = FakeWrapper()
    loc = Locator(w, "div")

    filtered = loc.filter(has_text="A")
    assert len(filtered) == 1


def test_filter_by_attribute():
    class W(FakeWrapper):
        def find_all(self, locator):
            return [FakeEl(attrs={"role": "button"}), FakeEl(attrs={"role": "input"})]

    w = W()
    loc = Locator(w, "div")
    out = loc.filter(has_attribute=("role", "button"))
    assert len(out) == 1


def test_filter_by_regex():
    class W(FakeWrapper):
        def find_all(self, locator):
            return [FakeEl("User 123"), FakeEl("No match")]

    w = W()
    loc = Locator(w, "div")
    out = loc.filter(has_regex=r"\d+")
    assert len(out) == 1


# -------------------------------------------------------------
# 9. first_filtered / last_filtered
# -------------------------------------------------------------
def test_first_filtered_raises_error_when_empty():
    w = FakeWrapper()
    loc = Locator(w, "div")
    with pytest.raises(AssertionError):
        loc.first_filtered(has_text="NO MATCH")


def test_last_filtered():
    w = FakeWrapper()
    loc = Locator(w, "div")

    out = loc.last_filtered(has_text="A")
    assert isinstance(out, Locator)


# -------------------------------------------------------------
# 10. nth(), first(), last(), count()
# -------------------------------------------------------------
def test_nth():
    w = FakeWrapper()
    loc = Locator(w, "div")
    nth = loc.nth(1)
    assert nth.index == 1


def test_first():
    w = FakeWrapper()
    loc = Locator(w, "div")
    f = loc.first()
    assert f.index == 0


def test_last():
    w = FakeWrapper()
    loc = Locator(w, "div")
    lst = loc.last()
    assert lst.index == 2  # because find_all returns 3 elements


def test_count():
    w = FakeWrapper()
    loc = Locator(w, "div")
    assert loc.count() == 3
