import os

from nrobo.core import settings
from nrobo.helpers.logging_helper import get_logger

logger = get_logger(name=settings.NROBO_APP)


def has_pytest_tests(test_dir="tests") -> bool:
    test_dir = os.path.abspath(test_dir)
    for root, _, files in os.walk(test_dir):
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                logger.debug(f"✅ Found test file: {os.path.join(root, f)}")
                return True
    return False
