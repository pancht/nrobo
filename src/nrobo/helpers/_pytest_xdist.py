import os


def is_running_with_xdist() -> bool:
    return "PYTEST_XDIST_WORKER" in os.environ