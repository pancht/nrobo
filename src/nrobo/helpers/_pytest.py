from _pytest.config import ExitCode
from _pytest.nodes import Item


def extract_test_name(item: Item) -> str:
    """
    Extracts a clean test method name (optionally with class) from pytest item.nodeid. # noqa: E501
    Handles parametrize, class methods, standalone functions.
    """
    nodeid = item.nodeid  # e.g. tests/test_file.py::TestClass::test_method[param]  # noqa: E501
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


def should_proceed(exit_code) -> bool:
    """Return True if further steps (e.g. report generation) should continue."""  # noqa: E501

    if isinstance(exit_code, int):
        try:
            exit_code = ExitCode(exit_code)
        except ValueError:
            return False  # Unknown code → stop

    return exit_code in (
        ExitCode.OK,
        ExitCode.NO_TESTS_COLLECTED,
        ExitCode.TESTS_FAILED,
    )  # noqa: E501


def no_execution_key_found(args: list):
    return any("--co" == arg for arg in args)
