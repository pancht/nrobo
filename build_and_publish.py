#!/usr/bin/env python3
"""
Auto-fetch latest version from PyPI/TestPyPI,
increment version, build, and ask confirmation before uploading.

Usage:
  python build_and_publish.py [--level patch|minor|major] [--test]
"""

import sys
import subprocess
import requests
import tomlkit
from pathlib import Path

PYPROJECT = Path("pyproject.toml")
PACKAGE_NAME = "nrobo"

def bump_version(version: str, level: str = "patch") -> str:
    major, minor, patch = map(int, version.split("."))
    if level == "major":
        major += 1; minor = patch = 0
    elif level == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"

def get_latest_pypi_version(package: str, test=False) -> str:
    """Fetch latest version from PyPI or TestPyPI API."""
    url = f"https://test.pypi.org/pypi/{package}/json" if test else f"https://pypi.org/pypi/{package}/json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("info", {}).get("version", "0.0.0")
    except Exception as e:
        print(f"⚠️ Could not fetch latest version: {e}")
    return "0.0.0"

def main():
    level = "patch"
    test_mode = "--test" in sys.argv
    if "--minor" in sys.argv: level = "minor"
    if "--major" in sys.argv: level = "major"

    # Load local version
    doc = tomlkit.parse(PYPROJECT.read_text())
    local_version = doc["project"]["version"]

    # Fetch latest version
    latest_version = get_latest_pypi_version(PACKAGE_NAME, test=test_mode)
    print(f"\n📦 Latest {PACKAGE_NAME} version on {'TestPyPI' if test_mode else 'PyPI'}: {latest_version}")
    print(f"🧩 Local pyproject version: {local_version}")

    # Decide bump
    if tuple(map(int, local_version.split("."))) <= tuple(map(int, latest_version.split("."))):
        new_version = bump_version(latest_version, level)
        print(f"⬆️  Auto-bumping version to: {new_version}")
    else:
        new_version = local_version
        print(f"✅ Local version ({local_version}) is newer, keeping as-is.")

    # Update pyproject.toml
    doc["project"]["version"] = new_version
    PYPROJECT.write_text(tomlkit.dumps(doc))

    # Build
    print("\n🔧 Building package...")
    subprocess.run([sys.executable, "-m", "build"], check=True)

    # Confirm before upload
    repo = "testpypi" if test_mode else "pypi"
    print(f"\n⚠️ Ready to upload version {new_version} to {repo}.")
    confirm = input("Do you want to continue with the upload? (y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("❌ Upload cancelled.")
        return

    print(f"📤 Uploading to {repo}...")
    subprocess.run([sys.executable, "-m", "twine", "upload", "--repository", repo, "dist/*"], check=True)

    print(f"\n✅ Version {new_version} successfully uploaded to {repo}!")

if __name__ == "__main__":
    main()
