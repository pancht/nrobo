import argparse

from nrobo.generators.page_generator import generate_page_file


def run(args):
    """
    Handle 'nrobo generate' CLI commands.
    Example:
        nrobo generate page LoginPage
    """
    parser = argparse.ArgumentParser(description="Generate nRobo components (Page, Locators, etc.)")

    # ------------------------------------------------------------------
    # Subcommand: page
    # ------------------------------------------------------------------
    parser.add_argument("page", help="Generate a new Page Object class and associated locator file")
    parser.add_argument("name", help="Name of the Page class to generate (e.g., LoginPage)")

    # ------------------------------------------------------------------
    # Parse args and dispatch
    # ------------------------------------------------------------------
    parsed_args = parser.parse_args(args)

    if parsed_args.page:
        generate_page_file(parsed_args.name)
    else:
        parser.print_help()  # pragma: no cover
