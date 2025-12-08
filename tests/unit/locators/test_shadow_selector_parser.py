from nrobo.locators.shadow_selector_parser import ShadowSelectorParser


def test_parse_basic_shadow_selector():
    selector = "shadow::#a >>> .b >>> button"
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#a", ".b", "button"]


def test_parse_multiple_shadow_prefixes():
    selector = "shadow::shadow::#root >>> .item"
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#root", ".item"]


def test_parse_with_whitespace():
    selector = "  shadow:: #a   >>>   .b    >>>   button   "
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#a", ".b", "button"]


def test_parse_no_shadow_operator():
    selector = "shadow::#only"
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#only"]


def test_parse_without_shadow_prefix():
    selector = "#a >>> .b >>> span"
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#a", ".b", "span"]


def test_parse_consecutive_separators():
    selector = "shadow::#a >>> >>> .b"
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#a", ".b"]  # empty segments removed


def test_parse_empty_string():
    result = ShadowSelectorParser.parse("")
    assert result == []


def test_parse_whitespace_only():
    result = ShadowSelectorParser.parse("   ")
    assert result == []


def test_parse_complex_selector():
    selector = "shadow::#root >>> div > span.title >>> button.primary"
    result = ShadowSelectorParser.parse(selector)
    assert result == ["#root", "div > span.title", "button.primary"]
