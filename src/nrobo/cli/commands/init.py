import argparse
import os

import yaml
from jinja2 import Template

from nrobo.core import settings
from nrobo.helpers.playwright_helper import install_playwright_browsers
from nrobo.utils.command_utils import initialize_project

PROJECT_TEMPLATE_PATH = (
    settings.BASE_DIR / "nrobo" / "templates" / "nrobo_project_template.yaml"
)  # noqa: E225


def load_and_inject_template(template_path, project_name):
    with open(template_path, "r") as file:
        template_str = file.read()
    rendered = Template(template_str).render(project_name=project_name)
    return yaml.safe_load(rendered)


def create_directories(base_path, folders):
    for folder in folders:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        print(f"📁 Created directory: {path}")


def create_files(base_path, files):
    for filepath, filecontent in files.items():
        path = os.path.join(base_path, filepath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            file.write(filecontent)
        print(f"📝 Created file: {path}")


def init_project(template_path, app_name, base_path="."):
    print("🚀 Initializing project structure...")
    template = load_and_inject_template(template_path, project_name=app_name)

    project_name = template.get("project", {}).get("name", "nrobo_project")
    print(f"📦 Project Name: {project_name}")

    folders = template.get("folders", [])
    files = template.get("files", {})

    create_directories(base_path, folders)
    create_files(base_path, files)

    initialize_project()

    install_playwright_browsers()

    print("✅ Initialization complete!")


def run(args):
    parser = argparse.ArgumentParser(description=f"{settings.NROBO_APP} project initializer")
    parser.add_argument("--app", required=True, type=str, help="App name (used as project name)")
    parsed_args = parser.parse_args(args)

    init_project(PROJECT_TEMPLATE_PATH, parsed_args.app)
