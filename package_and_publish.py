#!/usr/bin/env python3
"""
Auto-fetch latest version from PyPI/TestPyPI,
bump version, build package, and upload — with confirmation.

Usage:
  python build_and_publish.py [--level patch|minor|major] [--test] [--dry]
"""

import shutil
import subprocess
import sys
from pathlib import Path

import requests
import tomlkit
from packaging.version import parse as parse_version
from termcolor import cprint
from argparse import ArgumentParser

from nrobo.utils.update_version_utils import update_version_file

PYPROJECT = Path("pyproject.toml")
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


def get_latest_pypi_version(package: str, test=False) -> str:
    url = (
        f"https://test.pypi.org/pypi/{package}/json"
        if test
        else f"https://pypi.org/pypi/{package}/json"
    )
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("info", {}).get("version", "0.0.0")
    except Exception as e:
        cprint(f"⚠️ Could not fetch latest version: {e}", "yellow")
    return "0.0.0"


def clear_dist_folder():
    dist_path = Path("dist")
    if dist_path.exists() and dist_path.is_dir():
        cprint("🧹 Clearing old dist/ directory...", "cyan")
        shutil.rmtree(dist_path)


def show_git_changelog():
    cprint("\n📝 Last 5 commits:", "blue")
    subprocess.run(["git", "log", "--oneline", "HEAD~5..HEAD"])


def build_package():
    cprint("\n🔧 Building package...", "cyan")
    subprocess.run([sys.executable, "-m", "build"], check=True)


def upload_package(repo: str):
    cprint(f"\n📤 Uploading to {repo}...", "cyan")
    subprocess.run(
        [sys.executable, "-m", "twine", "upload", "--repository", repo, "dist/*"],
        check=True
    )


def main():
    parser = ArgumentParser(description="Build and upload nrobo to PyPI/TestPyPI.")
    parser.add_argument("--level", choices=["patch", "minor", "major"], default="patch", help="Version bump level")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI instead of PyPI")
    parser.add_argument("--dry", action="store_true", help="Dry-run: simulate actions without executing them")
    parser.add_argument("--no-git-log", action="store_true", help="Skip showing last Git commits")

    args = parser.parse_args()

    repo = "testpypi" if args.test else "pypi"
    dry = args.dry

    # Load current version
    doc = tomlkit.parse(PYPROJECT.read_text())
    local_version = doc["project"]["version"]

    # Fetch latest version online
    latest_version = get_latest_pypi_version(PACKAGE_NAME, test=args.test)
    cprint(f"\n📦 Latest {PACKAGE_NAME} on {repo}: {latest_version}", "green")
    cprint(f"🧩 Local pyproject.toml version: {local_version}", "cyan")

    # Decide on bump
    if parse_version(local_version) <= parse_version(latest_version):
        new_version = bump_version(latest_version, args.level)
        cprint(f"⬆️  Auto-bumping to version: {new_version}", "magenta")
    else:
        new_version = local_version
        cprint(f"✅ Local version is newer ({local_version}) — keeping as-is", "green")

    update_version_file(version_file_path=VERSION_FILE, new_version=new_version)

    if not args.no_git_log:
        show_git_changelog()

    if dry:
        cprint("\n💡 Dry-run mode enabled — no files written, no build or upload done.\n", "yellow")
        return

    # Update pyproject.toml
    doc["project"]["version"] = new_version
    PYPROJECT.write_text(tomlkit.dumps(doc))

    # Clean and build
    clear_dist_folder()
    build_package()

    # Confirm upload
    cprint(f"\n⚠️ Ready to upload version {new_version} to {repo}.", "red")
    confirm = input("Do you want to continue? (y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        cprint("❌ Upload cancelled.", "red")
        return

    upload_package(repo)

    cprint(f"\n✅ Version {new_version} successfully uploaded to {repo}!", "green")


if __name__ == "__main__":
    main()
