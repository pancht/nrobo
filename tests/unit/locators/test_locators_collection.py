from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest

from nrobo.locators.locator import Locator
from nrobo.locators.locator_collection import LocatorCollection


# ------------------------------------------------------------------------------
# Helpers: Fake WebElement and Fake Locator
# ------------------------------------------------------------------------------
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


class FakeEl:
    def __init__(self, text="", attrs=None, visible=True, enabled=True):
        self.text = text
        self.attrs = attrs or {}
        self.visible = visible
        self.enabled = enabled

    def get_attribute(self, name):
        return self.attrs.get(name)

    def is_displayed(self):
        return self.visible

    def is_enabled(self):
        return self.enabled


class FakeLocator:
    def __init__(
        self, text="", attrs=None, visible=True, enabled=True, by="css", value="x", index=None
    ):
        self.by = by
        self.value = value
        self.index = index
        self.wrapper = MagicMock()
        self.el = FakeEl(text=text, attrs=attrs, visible=visible, enabled=enabled)
        self.wrapper._resolve.return_value = self.el

    def click(self):
        self.el.clicked = True
        return self


# ------------------------------------------------------------------------------
# Basic Tests
# ------------------------------------------------------------------------------


def test_len_and_indexing():
    locs = [FakeLocator(), FakeLocator()]
    coll = LocatorCollection(locs)

    assert len(coll) == 2
    assert coll[0] is locs[0]
    assert coll[1] is locs[1]


def test_iteration():
    locs = [FakeLocator(), FakeLocator(), FakeLocator()]
    coll = LocatorCollection(locs)

    out = [l for l in coll]  # noqa: E741
    assert out == locs


# ------------------------------------------------------------------------------
# Selection Helpers
# ------------------------------------------------------------------------------


def test_first_last_nth():
    locs = [FakeLocator(text="1"), FakeLocator(text="2"), FakeLocator(text="3")]
    coll = LocatorCollection(locs)

    assert coll.first().el.text == "1"
    assert coll.last().el.text == "3"
    assert coll.nth(1).el.text == "2"

    with pytest.raises(AssertionError):
        LocatorCollection([]).first()


# ------------------------------------------------------------------------------
# Filter Tests
# ------------------------------------------------------------------------------


def test_filter_has_text():
    loc1 = FakeLocator(text="hello world")
    loc2 = FakeLocator(text="bye world")
    loc3 = FakeLocator(text="hello again")
    coll = LocatorCollection([loc1, loc2, loc3])

    out = coll.filter(has_text="hello")
    assert len(out) == 2
    assert out[0] is loc1
    assert out[1] is loc3


def test_filter_has_not_text():
    loc1 = FakeLocator(text="apple pie")
    loc2 = FakeLocator(text="banana pie")
    coll = LocatorCollection([loc1, loc2])

    out = coll.filter(has_not_text="banana")
    assert len(out) == 1
    assert out[0] is loc1


def test_filter_has_attribute():
    loc1 = FakeLocator(attrs={"role": "admin"})
    loc2 = FakeLocator(attrs={"role": "user"})
    coll = LocatorCollection([loc1, loc2])

    out = coll.filter(has_attribute=("role", "admin"))
    assert len(out) == 1
    assert out[0] is loc1


def test_filter_regex():
    loc1 = FakeLocator(text="Order #123")
    loc2 = FakeLocator(text="Order #999")
    coll = LocatorCollection([loc1, loc2])

    out = coll.filter(has_regex=r"#1")
    assert len(out) == 1
    assert out[0] is loc1


def test_filter_predicate():
    loc1 = FakeLocator(text="big")
    loc2 = FakeLocator(text="small")
    coll = LocatorCollection([loc1, loc2])

    out = coll.filter(has=lambda el: len(el.text) == 3)
    assert len(out) == 1
    assert out[0] is loc1


# ------------------------------------------------------------------------------
# Utility Helpers
# ------------------------------------------------------------------------------


def test_to_texts():
    loc1 = FakeLocator(text="a")
    loc2 = FakeLocator(text="b")
    coll = LocatorCollection([loc1, loc2])

    assert coll.to_texts() == ["a", "b"]


def test_to_attributes():
    loc1 = FakeLocator(attrs={"id": "1"})
    loc2 = FakeLocator(attrs={"id": "2"})
    coll = LocatorCollection([loc1, loc2])

    assert coll.to_attributes("id") == ["1", "2"]


def test_map():
    loc1 = FakeLocator(text="AAA")
    loc2 = FakeLocator(text="BBB")
    coll = LocatorCollection([loc1, loc2])

    out = coll.map(lambda el: el.text.lower())
    assert out == ["aaa", "bbb"]


def test_for_each():
    loc1 = FakeLocator()
    loc2 = FakeLocator()
    coll = LocatorCollection([loc1, loc2])

    calls = []
    coll.for_each(lambda l: calls.append(l))  # noqa: E741

    assert calls == [loc1, loc2]


def test_click_each():
    loc1 = FakeLocator()
    loc2 = FakeLocator()

    coll = LocatorCollection([loc1, loc2])
    coll.click_each()

    assert loc1.el.clicked is True
    assert loc2.el.clicked is True


# ------------------------------------------------------------------------------
# Assertion Helpers
# ------------------------------------------------------------------------------


def test_should_have_count():
    coll = LocatorCollection([FakeLocator(), FakeLocator()])
    coll.should_have_count(2)

    with pytest.raises(AssertionError):
        coll.should_have_count(3)


def test_texts_contain():
    loc1 = FakeLocator(text="hello world")
    loc2 = FakeLocator(text="hello test")
    coll = LocatorCollection([loc1, loc2])

    coll.texts_contain("hello")  # should not raise

    with pytest.raises(AssertionError):
        coll.texts_contain("bye")


def test_all_any_match():
    loc1 = FakeLocator(text="OK")
    loc2 = FakeLocator(text="Fine")
    coll = LocatorCollection([loc1, loc2])

    assert coll.all_match(lambda el: len(el.text) >= 2) is True
    assert coll.any_match(lambda el: el.text == "OK") is True
    assert coll.any_match(lambda el: el.text == "Missing") is False


# ------------------------------------------------------------------------------
# Sorting Tests
# ------------------------------------------------------------------------------


def test_sort_by_text():
    loc1 = FakeLocator(text="Charlie")
    loc2 = FakeLocator(text="Alice")
    loc3 = FakeLocator(text="Bob")

    coll = LocatorCollection([loc1, loc2, loc3])
    sorted_coll = coll.sort_by_text()

    assert sorted_coll.to_texts() == ["Alice", "Bob", "Charlie"]


def test_sorted_by_attribute():
    loc1 = FakeLocator(attrs={"id": "3"})
    loc2 = FakeLocator(attrs={"id": "1"})
    loc3 = FakeLocator(attrs={"id": "2"})

    coll = LocatorCollection([loc1, loc2, loc3])
    sorted_coll = coll.sorted_by_attribute("id")

    assert sorted_coll.to_attributes("id") == ["1", "2", "3"]


# ------------------------------------------------------------------------------
# Visibility / Enabled Tests
# ------------------------------------------------------------------------------


def test_filter_visible():
    loc1 = FakeLocator(visible=True)
    loc2 = FakeLocator(visible=False)

    coll = LocatorCollection([loc1, loc2])
    out = coll.filter_visible()

    assert len(out) == 1
    assert out[0] is loc1


def test_filter_enabled():
    loc1 = FakeLocator(enabled=True)
    loc2 = FakeLocator(enabled=False)

    coll = LocatorCollection([loc1, loc2])
    out = coll.filter_enabled()

    assert len(out) == 1
    assert out[0] is loc1


# ------------------------------------------------------------------------------
# Ordering Operators
# ------------------------------------------------------------------------------


def test_reverse():
    locs = [FakeLocator(text="1"), FakeLocator(text="2"), FakeLocator(text="3")]
    coll = LocatorCollection(locs)

    rev = coll.reverse()
    assert rev.to_texts() == ["3", "2", "1"]


def test_shuffle():
    # Hard to assert randomness; assert items preserved
    locs = [FakeLocator(text=str(i)) for i in range(5)]
    coll = LocatorCollection(locs)

    shuffled = coll.shuffle()
    assert sorted(l.el.text for l in shuffled) == ["0", "1", "2", "3", "4"]  # noqa: E741


def test_random():
    locs = [FakeLocator(), FakeLocator()]
    coll = LocatorCollection(locs)
    assert coll.random() in locs

    with pytest.raises(AssertionError):
        LocatorCollection([]).random()


# ------------------------------------------------------------------------------
# Set Operators
# ------------------------------------------------------------------------------


def test_exclude_difference():
    l1 = FakeLocator(by="css", value="a", index=0)
    l2 = FakeLocator(by="css", value="b", index=1)
    l3 = FakeLocator(by="css", value="c", index=2)

    coll1 = LocatorCollection([l1, l2, l3])
    coll2 = LocatorCollection([l2])

    diff = coll1.difference(coll2)
    assert diff.locators == [l1, l3]


def test_intersection():
    l1 = FakeLocator(by="css", value="a", index=0)
    l2 = FakeLocator(by="css", value="b", index=1)

    coll1 = LocatorCollection([l1, l2])
    coll2 = LocatorCollection([l2])

    inter = coll1.intersection(coll2)
    assert inter.locators == [l2]


def test_union():
    l1 = FakeLocator(by="css", value="a", index=0)
    l2 = FakeLocator(by="css", value="b", index=1)
    l3 = FakeLocator(by="css", value="c", index=2)

    coll1 = LocatorCollection([l1, l2])
    coll2 = LocatorCollection([l2, l3])

    uni = coll1.union(coll2)

    assert len(uni) == 3
    assert set((l.by, l.value, l.index) for l in uni.locators) == {  # noqa: E741
        ("css", "a", 0),
        ("css", "b", 1),
        ("css", "c", 2),
    }


def test_unique():
    l1 = FakeLocator(by="css", value="a", index=0)
    l2 = FakeLocator(by="css", value="a", index=0)  # duplicate
    l3 = FakeLocator(by="css", value="b", index=1)

    coll = LocatorCollection([l1, l2, l3])
    uniq = coll.unique()

    assert len(uniq) == 2
    assert uniq.locators == [l1, l3]


# ------------------------------------------------------------------------------
# Index / Slice Operators
# ------------------------------------------------------------------------------


def test_filter_index():
    locs = [FakeLocator(text=str(i)) for i in range(5)]
    coll = LocatorCollection(locs)

    even = coll.filter_index(lambda i: i % 2 == 0)
    assert even.to_texts() == ["0", "2", "4"]


def test_slice():
    locs = [FakeLocator(text=str(i)) for i in range(5)]
    coll = LocatorCollection(locs)

    sliced = coll.slice(1, 4)
    assert sliced.to_texts() == ["1", "2", "3"]


# ------------------------------------------------------------------------------
# wait_for_count
# ------------------------------------------------------------------------------


def test_wait_for_count_success(monkeypatch):
    locs = [FakeLocator(), FakeLocator()]
    coll = LocatorCollection(locs)

    monkeypatch.setattr(coll, "locators", [1, 2])  # simulate stable count

    assert coll.wait_for_count(2, timeout=1) is coll


def test_wait_for_count_timeout(monkeypatch):
    locs = [FakeLocator()]
    coll = LocatorCollection(locs)

    with pytest.raises(AssertionError):
        coll.wait_for_count(expected=3, timeout=1)


def test_locator_collection_locator(fake_wrapper):
    # Create a base Locator
    base_locator = Locator(fake_wrapper, "div")

    # Create a LocatorCollection with one item
    collection = LocatorCollection([base_locator])

    # Call .locator() to chain a selector
    chained = collection.locator("span")

    # Assertions
    assert isinstance(chained, Locator)
    assert chained.selector == "span"
    assert chained.wrapper == fake_wrapper
