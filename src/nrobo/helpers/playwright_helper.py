# nrobo/helpers/playwright_helper.py
import json
import subprocess
from pathlib import Path


def is_playwright_installed() -> bool:
    """Check if playwright has installed its required browsers."""
    browser_cache = Path.home() / ".cache" / "ms-playwright"
    return browser_cache.exists() and any(browser_cache.iterdir())


def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    if is_playwright_installed():
        print("🟢 Playwright browsers already installed.")
        return
    try:
        print("🔧 Installing Playwright browsers via `playwright install`...")
        subprocess.run(["playwright", "install"], check=True)
        print("✅ Playwright browsers installed successfully.")
    except Exception as e:
        print(f"❌ Failed to install Playwright browsers: {e}")


def get_outdated_packages():
    """Return list of outdated packages as dicts."""
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Failed to list outdated packages: {e}")
        return []


def update_playwright_dependencies():
    target_packages = {"playwright", "pytest-playwright"}

    outdated = get_outdated_packages()
    to_update = [pkg for pkg in outdated if pkg["name"] in target_packages]

    if not to_update:
        print("✅ Playwright packages are already up to date.")
        return

    print("📦 Outdated packages found:")
    for pkg in to_update:
        print(f"• {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")

    print("\n🔄 Updating...")
    try:
        subprocess.run(["pip", "install", "-U", *target_packages], check=True)
        print("✅ Updated successfully.")
    except Exception as e:
        print(f"❌ Failed to update: {e}")
