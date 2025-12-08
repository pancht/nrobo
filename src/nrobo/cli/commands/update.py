import argparse
import subprocess

from nrobo.helpers.playwright_helper import (
    install_playwright_browsers,
    update_playwright_dependencies,
)
from nrobo.helpers.selenium_helper import update_selenium_dependencies


def run(args):
    parser = argparse.ArgumentParser(description="Update nrobo dependencies")
    parser.add_argument(
        "--playwright", action="store_true", help="Update Playwright and install browsers"
    )
    parser.add_argument("--selenium", action="store_true", help="Update Selenium and webdrivers")
    parser.add_argument("--self", action="store_true", help="Update nrobo itself")

    parsed = parser.parse_args(args)

    if parsed.playwright:
        print("🔄 Updating Playwright stack...")
        update_playwright_dependencies()
        install_playwright_browsers()

    if parsed.selenium:
        print("🔄 Updating Selenium stack...")
        update_selenium_dependencies()

    if parsed.self:
        print("🔄 Updating nrobo framework...")
        try:
            subprocess.run(["pip", "install", "--upgrade", "nrobo"], check=True)
            print("✅ Updated nrobo.")
        except Exception as e:
            print(f"❌ Failed to update nrobo: {e}")
