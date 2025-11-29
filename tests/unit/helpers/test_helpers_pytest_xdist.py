import os
from unittest.mock import patch

from nrobo.helpers._pytest_xdist import is_running_with_xdist


def test_is_running_with_xdist_true():
    with patch.dict(os.environ, {"PYTEST_XDIST_WORKER": "gw0"}):
        assert is_running_with_xdist() is True


def test_is_running_with_xdist_false():
    with patch.dict(os.environ, {}, clear=True):
        assert is_running_with_xdist() is False
