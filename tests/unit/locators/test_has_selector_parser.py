from nrobo.locators.has_selector_parser import HasSelectorParser


def test_split_basic():
    base, inside = HasSelectorParser.split("div:has(span)")
    assert base == "div"
    assert inside == "span"


def test_split_complex_inside():
    base, inside = HasSelectorParser.split("ul:has(li.active[data-id='12'])")
    assert base == "ul"
    assert inside == "li.active[data-id='12']"


def test_split_no_base_selector():
    base, inside = HasSelectorParser.split(":has(.item)")
    assert base == ""  # because before :has( is empty
    assert inside == ".item"


def test_split_nested_has():
    base, inside = HasSelectorParser.split("div:has(span:has(a))")
    assert base == "div"
    assert inside == "span:has(a"  # correct for your current parser


def test_split_multiple_trailing_parens():
    base, inside = HasSelectorParser.split("div:has((a)))")
    assert base == "div"
    assert inside == "(a"


def test_split_very_complex():
    selector = "main:has(section > div.item:not(.disabled)[data-x='y'])"
    base, inside = HasSelectorParser.split(selector)

    assert base == "main"
    assert inside == "section > div.item:not(.disabled)[data-x='y']"
