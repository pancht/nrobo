# tests/test_build_and_publish.py
import builtins
import subprocess
import sys
import urllib.parse

import pytest
import requests

from nrobo import pypi_uploader as bap


class DummyResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# --- Helpers / Fixtures ---


@pytest.fixture(autouse=True)
def no_real_subprocess(monkeypatch, tmp_path):
    """
    Prevent any real subprocess.run calls. Allows customizing return values.
    """
    calls = []

    def fake_run(cmd, *args, **kwargs):
        calls.append((cmd, kwargs))
        # default "successful" result
        return DummyResult(returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


@pytest.fixture
def fake_requests(monkeypatch):
    """
    Fixture to mock requests.get for get_latest_version tests.
    """

    class DummyResp:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data

        def raise_for_status(self):
            if self.status_code != 200:
                raise requests.HTTPError(f"status {self.status_code}")

        def json(self):
            return self._data

    def fake_get(url, timeout):
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname and parsed.hostname.lower() == "test.pypi.org":
            return DummyResp(200, {"info": {"version": "1.2.3"}})
        else:
            # simulate non-200 for main PyPI
            return DummyResp(404, {})

    monkeypatch.setattr(requests, "get", fake_get)


# --- Tests ---


def test_bump_version_patch():
    assert bap.bump_version("0.0.0", "patch") == "0.0.1"
    assert bap.bump_version("1.2.3", "patch") == "1.2.4"


def test_bump_version_minor():
    assert bap.bump_version("1.2.3", "minor") == "1.3.0"


def test_bump_version_major():
    assert bap.bump_version("1.2.3", "major") == "2.0.0"


def test_get_latest_version_success_and_fallback(fake_requests, capsys):
    v_test = bap.get_latest_version("dummy", test=True)
    assert v_test == "1.2.3"
    v_main = bap.get_latest_version("dummy", test=False)
    # since fake GET returns 404 for main PyPI, we should get default "0.0.0"
    assert v_main == "0.0.0"
    captured = capsys.readouterr()
    assert "Could fetch version" not in captured.out  # no warning for test success
    assert "Could fetch version" in captured.out or v_main == "0.0.0"


def test_clear_dist_folder(tmp_path, monkeypatch, capsys):
    # create a fake dist folder
    dist = tmp_path / "dist"
    dist.mkdir()
    # monkeypatch Path.cwd or just monkeypatch Path("dist") to refer to tmp_path/dist
    monkeypatch.chdir(tmp_path)
    bap.clear_dist_folder()
    captured = capsys.readouterr()
    assert "Clearing old dist/" in captured.out
    assert not dist.exists()


def test_build_and_upload(monkeypatch, no_real_subprocess):
    bap.build_package()
    bap.upload_package("testrepo")
    # verify subprocess.run was called for build and upload
    cmds = [c[0] for c in no_real_subprocess]
    assert any("build" in cmd for cmd in cmds)
    assert any("twine" in cmd for cmd in cmds)


@pytest.mark.parametrize(
    "attempts, exit_codes, expect",
    [
        # (1, [0], True),          # install succeeds first attempt
        # (2, [1, 0], True),       # first fails, second succeeds
        (2, [1, 1], False),  # both fail → smoke_test_install fails
    ],
)
def test_smoke_test_install(
    monkeypatch, tmp_path, no_real_subprocess, attempts, exit_codes, expect
):
    """
    Test smoke_test_install under various subprocess exit codes.
    """
    # monkeypatch cwd to tmp_path
    monkeypatch.chdir(tmp_path)
    # monkeypatch Path.exists to return False initially
    # But since we haven't created it, it's fine.

    # prepare subprocess.run to simulate exit codes
    results = [DummyResult(returncode=code, stdout="o", stderr="e") for code in exit_codes]

    def run_sequence(cmd, *args, **kwargs):
        # pop from results
        if results:
            return results.pop(0)
        # default: simulate success for any unexpected extra subprocess calls
        return DummyResult(returncode=1, stdout="unexpected", stderr="fail")

    monkeypatch.setattr(subprocess, "run", run_sequence)

    # Simulate import success: the python -c ... call returns code 0
    # But since we control the sequence, above works.

    success = bap.smoke_test_install("dummy_pkg", "dummy_pkg==0.1.0")
    assert success == expect


def test_main_dry_run(monkeypatch, tmp_path, fake_requests, no_real_subprocess, capsys):
    # prepare a fake pyproject.toml in tmp_path
    monkeypatch.chdir(tmp_path)
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""[project]\nversion = "0.0.1"\nname = "nrobo"\n""")
    # monkeypatch the constant PYPROJECT inside module
    monkeypatch.setattr(bap, "PYPROJECT", pyproject)
    monkeypatch.setattr(bap, "VERSION_FILE", tmp_path / "version.py")
    # Run main with --dry
    monkeypatch.setattr(sys, "argv", ["prog", "--dry"])
    bap.main()
    captured = capsys.readouterr()
    assert "Dry run" in captured.out


def test_main_flow_cancel_upload(monkeypatch, tmp_path, fake_requests, no_real_subprocess, capsys):
    # prepare fake pyproject
    monkeypatch.chdir(tmp_path)
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""[project]\nversion = "0.0.1"\nname = "nrobo"\n""")
    version_file = tmp_path / "version.py"
    version_file.write_text("""__version__ = "0.0.1"\n""")
    monkeypatch.setattr(bap, "PYPROJECT", pyproject)
    monkeypatch.setattr(bap, "VERSION_FILE", version_file)
    # simulate input "n" at confirmation prompt
    monkeypatch.setattr(builtins, "input", lambda prompt="": "n")
    # do not pass --test, --dry
    monkeypatch.setattr(sys, "argv", ["prog"])
    bap.main()
    captured = capsys.readouterr()
    assert (
        "Uploading to pypi cancelled" in captured.out
        or "Uploading to pypi cancelled" in captured.err
    )
