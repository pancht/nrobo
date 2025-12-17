import sys


def has_dev_flag() -> bool:
    for arg in sys.argv:
        if arg == "--dev":
            return True
        if arg.startswith("--dev="):
            return arg.split("=", 1)[1].lower() in ("1", "true", "yes")
    return False
