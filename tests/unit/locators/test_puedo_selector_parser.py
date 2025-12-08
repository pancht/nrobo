from nrobo.locators.pseudo_selector_parser import PseudoSelectorParser


def test_split_basic_pseudo():
    base, pseudos = PseudoSelectorParser.split("button:visible")
    assert base == "button"
    assert pseudos == [":visible"]


def test_split_multiple_pseudos():
    base, pseudos = PseudoSelectorParser.split("button:visible:enabled:focus")
    assert base == "button"
    assert pseudos == [":visible", ":enabled", ":focus"]


def test_split_not_selector():
    base, pseudos = PseudoSelectorParser.split("div:not(.hidden)")
    assert base == "div"
    assert pseudos == [":not(.hidden)"]


def test_split_mixed_pseudos():
    base, pseudos = PseudoSelectorParser.split("section:not(.disabled):visible")
    assert base == "section"
    assert pseudos == [":not(.disabled)", ":visible"]


def test_split_starts_with_pseudo():
    base, pseudos = PseudoSelectorParser.split(":visible")
    assert base == "*"
    assert pseudos == [":visible"]


def test_split_empty_base_with_not():
    base, pseudos = PseudoSelectorParser.split(":not(.active)")
    assert base == "*"
    assert pseudos == [":not(.active)"]


def test_split_whitespace():
    base, pseudos = PseudoSelectorParser.split("  button  :   visible  ")
    assert base == "button"
    assert pseudos == [":visible"]


def test_split_complex_not():
    base, pseudos = PseudoSelectorParser.split("input:not(div > .something[data-x='y'])")
    assert base == "input"
    assert pseudos == [":not(div > .something[data-x='y'])"]


def test_split_no_pseudo():
    base, pseudos = PseudoSelectorParser.split("button")
    assert base == "button"
    assert pseudos == []


def test_split_empty_string():
    base, pseudos = PseudoSelectorParser.split("")
    assert base == "*"
    assert pseudos == []
