import sys

from nrobo.helpers.nrobo_helper import has_dev_flag


def test_has_dev_flag_plain_dev(monkeypatch):
    """Covers: arg == '--dev' → True"""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--dev"])
    assert has_dev_flag() is True


def test_has_dev_flag_equals_true(monkeypatch):
    """Covers: --dev=true → True"""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--dev=true"])
    assert has_dev_flag() is True


def test_has_dev_flag_equals_one(monkeypatch):
    """Covers: --dev=1 → True"""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--dev=1"])
    assert has_dev_flag() is True


def test_has_dev_flag_equals_yes(monkeypatch):
    """Covers: --dev=yes → True"""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--dev=yes"])
    assert has_dev_flag() is True


def test_has_dev_flag_equals_false(monkeypatch):
    """Covers: --dev=false → False"""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--dev=false"])
    assert has_dev_flag() is False


def test_has_dev_flag_not_present(monkeypatch):
    """Covers: loop completes → return False"""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--engine=selenium"])
    assert has_dev_flag() is False
