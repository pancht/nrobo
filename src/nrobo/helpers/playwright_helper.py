# nrobo/helpers/playwright_helper.py

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
