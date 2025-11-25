from _pytest.nodes import Item


def extract_test_name(item: Item) -> str:
    """
    Extracts a clean test method name (optionally with class) from pytest item.nodeid.
    Handles parametrize, class methods, standalone functions.
    """
    nodeid = item.nodeid  # e.g. tests/test_file.py::TestClass::test_method[param]
    parts = nodeid.split("::")

    if len(parts) == 3:
        # Format: file::class::method
        _, cls, method = parts
        return f"{cls}_{method}"
    elif len(parts) == 2:
        # Format: file::method
        _, method = parts
        return method
    else:
        # Fallback to last part
        return parts[-1]
