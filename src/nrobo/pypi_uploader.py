#!/usr/bin/env python3
"""
Auto-fetch latest version from PyPI/TestPyPI,
bump version, build package, upload — with optional smoke-test before real PyPI upload.

Usage:
  python build_and_publish.py [--level patch|minor|major] [--test] [--smoke] [--dry]
"""

import shutil
import subprocess
import sys
import tempfile
import time
from argparse import ArgumentParser
from pathlib import Path

import requests
import tomlkit
from termcolor import cprint

from nrobo.utils.update_version_utils import update_version_file

PYPROJECT = Path("pyproject.toml").resolve()
PACKAGE_NAME = "nrobo"
VERSION_FILE = Path("src") / PACKAGE_NAME / "version.py"


def bump_version(version: str, level: str = "patch") -> str:
    major, minor, patch = map(int, version.split("."))
    if level == "major":
        major += 1
        minor = patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def get_latest_version(package: str, test=False) -> str:
    url = f"https://{'test.' if test else ''}pypi.org/pypi/{package}/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json().get("info", {}).get("version", "0.0.0")
    except Exception as e:
        cprint(f"⚠️ Could not fetch version from {'Test' if test else ''}PyPI: {e}", "yellow")
        return "0.0.0"


def clear_dist_folder():
    dist = Path("dist")
    if dist.exists():
        cprint("🧹 Clearing old dist/ directory...", "cyan")
        shutil.rmtree(dist)


def build_package():
    cprint("🔧 Building package...", "cyan")
    subprocess.run([sys.executable, "-m", "build"], check=True)


def upload_package(repo: str):
    cprint(f"📤 Uploading to {repo}...", "cyan")
    subprocess.run(
        [sys.executable, "-m", "twine", "upload", "--repository", repo, "dist/*"], check=True
    )


def smoke_test_install(package_name: str, version_tag: str) -> bool:
    cprint("🧪 Smoke-testing install in isolated temp project...", "cyan")

    # Create isolated temp dir for full project + venv
    with tempfile.TemporaryDirectory(prefix=".smoke_test_") as project_dir:
        project_dir = Path(project_dir)
        venv_dir = project_dir / ".venv"

        # Step 1: Create venv
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        bin_dir = "Scripts" if sys.platform.startswith("win") else "bin"
        pip = venv_dir / bin_dir / "pip"
        python = venv_dir / bin_dir / "python"
        nrobo_cmd = venv_dir / bin_dir / "nrobo"

        # Step 2: Install from TestPyPI
        install_cmd = [
            str(pip),
            "install",
            "-i",
            "https://test.pypi.org/simple/",
            "--extra-index-url",
            "https://pypi.org/simple",
            version_tag,
        ]
        for attempt in range(2):
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                break
            cprint(f"⚠️ Install failed (attempt {attempt + 1}): {result.stderr}", "yellow")
            time.sleep(5)
        else:
            cprint("❌ Failed to install package from TestPyPI", "red")
            return False

        # Step 3: Import test
        import_test = f"from {package_name}.version import __version__; print(__version__)"
        result = subprocess.run([str(python), "-c", import_test], capture_output=True, text=True)
        if result.returncode != 0:
            cprint(f"❌ Import test failed:\n{result.stderr}", "red")
            return False

        # Step 4: `nrobo init --app demo` inside temp project dir
        cprint("🔧 Running `nrobo init --app demo`...", "cyan")
        result = subprocess.run(
            [str(nrobo_cmd), "init", "--app", "demo"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            cprint(f"❌ `nrobo init` failed:\n{result.stderr}", "red")
            return False

        # Step 5: run `nrobo` to verify CLI
        cprint("🚀 Running `nrobo` to confirm CLI works...", "cyan")
        result = subprocess.run([str(nrobo_cmd)], cwd=project_dir, capture_output=True, text=True)
        if result.returncode != 0:
            cprint(f"❌ `nrobo` CLI failed:\n{result.stderr}", "red")
            return False

        cprint("✅ Smoke test passed — install, init, and CLI ran successfully!", "green")
        return True


def main():
    parser = ArgumentParser()
    parser.add_argument("--level", choices=["patch", "minor", "major"], default="patch")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--smoke", action="store_true", help="Smoke test after TestPyPI upload")
    parser.add_argument("--dry", action="store_true", help="Dry run (skip build/upload)")
    parser.add_argument("--no-git-log", action="store_true", help="Skip showing recent git log")

    args = parser.parse_args()

    doc = tomlkit.parse(PYPROJECT.read_text())
    local_version = doc["project"]["version"]

    latest_pypi = get_latest_version(PACKAGE_NAME)
    latest_testpypi = get_latest_version(PACKAGE_NAME, test=True)

    bump_pypi = bump_version(latest_pypi, args.level)
    bump_testpypi = bump_version(latest_testpypi, args.level)

    cprint(f"\n📦 Local: {local_version}", "cyan")
    cprint(f"🌐 PyPI: {latest_pypi}, TestPyPI: {latest_testpypi}", "green")
    cprint(f"⬆️  New versions → PyPI: {bump_pypi}, TestPyPI: {bump_testpypi}", "magenta")

    if not args.no_git_log:
        subprocess.run(["git", "log", "--oneline", "HEAD~5..HEAD"])

    if args.dry:
        cprint("💡 Dry run: skipping build/upload", "yellow")
        return

    # Update files for TestPyPI first
    update_version_file(VERSION_FILE, bump_testpypi)
    doc["project"]["version"] = bump_testpypi
    PYPROJECT.write_text(tomlkit.dumps(doc))

    clear_dist_folder()
    build_package()
    upload_package("testpypi")

    tag = f"{PACKAGE_NAME}=={bump_testpypi}"
    if not smoke_test_install(PACKAGE_NAME, tag):
        cprint("❌ Smoke test failed — aborting", "red")
        sys.exit(1)
    confirm = input("Proceed building package for pypi? [y/N]: ").strip().lower()
    if confirm not in ("y", "yes"):
        cprint("🚫 Uploading to pypi cancelled", "red")
        return

    if not args.test:
        cprint("✅ Test upload complete. Proceeding to PyPI...", "cyan")
        update_version_file(VERSION_FILE, bump_pypi)
        doc["project"]["version"] = bump_pypi
        PYPROJECT.write_text(tomlkit.dumps(doc))

        clear_dist_folder()
        build_package()

        cprint(f"\n⚠️ Confirm upload to PyPI for version {bump_pypi}", "red")
        confirm = input("Proceed uploading to pypi? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            cprint("🚫 Uploading to pypi cancelled", "red")
            return

        upload_package("pypi")
        cprint(f"🎉 Uploaded {PACKAGE_NAME} v{bump_pypi} to PyPI", "green")


if __name__ == "__main__":
    main()
