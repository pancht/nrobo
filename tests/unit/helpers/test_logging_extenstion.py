import importlib
import logging
import sys


def test_import_time_guards_are_covered(monkeypatch):
    """
    Covers import-time guarded branches:
      - if not hasattr(logging, "DEV_DEBUG")
      - if not hasattr(logging.Logger, "dev_debug")
    """

    # 1️⃣ Remove previously injected attributes
    monkeypatch.delattr(logging, "DEV_DEBUG", raising=False)
    monkeypatch.delattr(logging.Logger, "dev_debug", raising=False)

    # 2️⃣ Force fresh import
    module_name = "nrobo.helpers.logging_extensions"
    sys.modules.pop(module_name, None)

    module = importlib.import_module(module_name)

    # 3️⃣ Assertions → guarded branches executed
    assert hasattr(logging, "DEV_DEBUG")
    assert logging.DEV_DEBUG == module.DEV_DEBUG

    assert hasattr(logging.Logger, "dev_debug")
    assert callable(logging.Logger.dev_debug)
