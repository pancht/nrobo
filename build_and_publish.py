#!/usr/bin/env python3
"""
Auto-fetch latest version from PyPI/TestPyPI,
increment version, build, and ask confirmation before uploading.

Usage:
  python build_and_publish.py [--level patch|minor|major] [--test]
"""
from pathlib import Path
import shutil
import sys
import subprocess
import requests
import tomlkit

PYPROJECT = Path("pyproject.toml")
PACKAGE_NAME = "nrobo"


def bump_version(version: str, level: str = "patch") -> str:  # pylint: disable=C0116
    major, minor, patch = map(int, version.split("."))
    if level == "major":
        major += 1
        minor = patch = 0  # pylint: disable=C0321
    elif level == "minor":
        minor += 1
        patch = 0  # pylint: disable=C0321
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def get_latest_pypi_version(package: str, test=False) -> str:
    """Fetch latest version from PyPI or TestPyPI API."""
    url = f"https://test.pypi.org/pypi/{package}/json" if test else f"https://pypi.org/pypi/{package}/json"  # pylint: disable=C0301
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("info", {}).get("version", "0.0.0")
    except Exception as e:  # pylint: disable=W0718
        print(f"⚠️ Could not fetch latest version: {e}")
    return "0.0.0"


def clear_dist_folder():  # pylint: disable=C0116
    dist_path = Path("dist")
    if dist_path.exists() and dist_path.is_dir():
        print("🧹 Clearing old dist/ directory...")
        shutil.rmtree(dist_path)


def main():  # pylint: disable=C0116
    level = "patch"
    test_mode = "--test" in sys.argv
    if "--minor" in sys.argv: level = "minor"  # pylint: disable=C0321
    if "--major" in sys.argv: level = "major"  # pylint: disable=C0321

    # Load local version
    doc = tomlkit.parse(PYPROJECT.read_text())  # pylint: disable=W1514
    local_version = doc["project"]["version"]

    # Fetch latest version
    latest_version = get_latest_pypi_version(PACKAGE_NAME, test=test_mode)
    print(
        f"\n📦 Latest {PACKAGE_NAME} version on {'TestPyPI' if test_mode else 'PyPI'}: {latest_version}")  # pylint: disable=C0301
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
    PYPROJECT.write_text(tomlkit.dumps(doc))  # pylint: disable=W1514

    # Clean dist before build
    clear_dist_folder()

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
    subprocess.run([sys.executable, "-m", "twine", "upload", "--repository", repo, "dist/*"],
                   check=True)  # pylint: disable=C0301

    print(f"\n✅ Version {new_version} successfully uploaded to {repo}!")


if __name__ == "__main__":
    main()
