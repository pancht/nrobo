import os


def is_running_with_xdist() -> bool:
    return "PYTEST_XDIST_WORKER" in os.environ


def grab_worker_id() -> str:
    return os.environ.get("PYTEST_XDIST_WORKER", "master")
