import argparse


def run(args):
    parser = argparse.ArgumentParser(description="Update nrobo dependencies")
    parser.add_argument(
        "--playwright", action="store_true", help="Update Playwright and install browsers"
    )

    parsed = parser.parse_args(args)

    if parsed.playwright:
        from nrobo.helpers.playwright_helper import (
            install_playwright_browsers,
            update_playwright_dependencies,
        )

        update_playwright_dependencies()
        install_playwright_browsers()
