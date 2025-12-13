import re
from pathlib import Path

PAGE_TEMPLATE = """\
from nrobo.pages.base_page import BasePage
from pages.{snake_name}_locators import {class_name}Locators


class {class_name}(BasePage):
    \"\"\"
    Page Object for {class_name}.
    Extend with actions and assertions for this page.
    \"\"\"

    loc = {class_name}Locators()

    def open_page(self):
        # Example:
        # return self.open("https://example.com/login")
        pass

    # Example action:
    # def login(self, user, pwd):
    #     self.locator(self.loc.USERNAME).fill(user)
    #     self.locator(self.loc.PASSWORD).fill(pwd)
    #     self.locator(self.loc.LOGIN_BTN).click()
    #     return self
"""

LOCATORS_TEMPLATE = """\
\"\"\"Locators for {class_name} Page.\"\"\"

class {class_name}Locators:
    # Add your page-specific selectors here.

    # Example:
    # USERNAME = "#username"
    # PASSWORD = "#password"
    # LOGIN_BTN = "button:has-text('Login')"

    pass
"""


def to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def generate_page_file(page_name: str):
    class_name = page_name
    snake_name = to_snake(page_name)

    pages_dir = Path("pages")
    pages_dir.mkdir(exist_ok=True)

    # ----------------------------------
    # Generate Page File
    # ----------------------------------
    page_file = pages_dir / f"{snake_name}.py"
    if not page_file.exists():
        page_file.write_text(PAGE_TEMPLATE.format(class_name=class_name, snake_name=snake_name))
        print(f"✔ Created page: {page_file}")
    else:
        print(f"⚠ Page already exists: {page_file}")

    # ----------------------------------
    # Generate Locator File
    # ----------------------------------
    locator_file = pages_dir / f"{snake_name}_locators.py"
    if not locator_file.exists():
        locator_file.write_text(LOCATORS_TEMPLATE.format(class_name=class_name))
        print(f"✔ Created locator file: {locator_file}")
    else:
        print(f"⚠ Locator file already exists: {locator_file}")
