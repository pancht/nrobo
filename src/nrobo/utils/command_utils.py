import importlib.resources as res
from pathlib import Path

from nrobo.core import settings
from nrobo.helpers.logging_helper import get_logger

logger = get_logger(name=settings.NROBO_APP)


def initialize_project():
    base_dir = Path.cwd()
    suites_dir = base_dir / settings.SUITES_DIR
    tests_dir = base_dir / settings.TESTS_DIR
    ui_dir = tests_dir / settings.UI_DIR
    api_dir = tests_dir / settings.API_DIR
    mobile_dir = tests_dir / settings.MOBILE_DIR
    reports_dir = base_dir / settings.HTML_REPORT_PATH
    allure_reports_dir = base_dir / settings.ALLURE_REPORT_DIR
    allure_results_dir = base_dir / settings.ALLURE_RESULTS_DIR
    logs_dir = base_dir / settings.LOG_DIR
    page_dir = base_dir / settings.PAGE_OBJECT_DIR
    # test_data_dir = base_dir / settings.TEST_DATA_DIR
    configs_dir = base_dir / "configs"

    suites_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    ui_dir.mkdir(parents=True, exist_ok=True)
    api_dir.mkdir(parents=True, exist_ok=True)
    mobile_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    allure_reports_dir.mkdir(parents=True, exist_ok=True)
    allure_results_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)
    # test_data_dir.mkdir(parents=True, exist_ok=True)
    configs_dir.mkdir(parents=True, exist_ok=True)

    # Copy template files from package templates
    with res.files("nrobo.templates").joinpath("sample_suite.yml").open("rb") as src:  # noqa: E501
        (suites_dir / "sample_suite.yml").write_bytes(src.read())

    with res.files("nrobo.templates").joinpath("test_sample.py").open("rb") as src:  # noqa: E501
        (ui_dir / "test_sample.py").write_bytes(src.read())

    with (
        res.files("nrobo.templates").joinpath("test_sample_another.py").open("rb") as src
    ):  # noqa: E501
        (ui_dir / "test_sample_another.py").write_bytes(src.read())

    logger.info(f"✨ {settings.NROBO_APP} project initialized!")
    logger.info("📁 Your nRobo project structure has been created!")
    logger.info("📘 For a quick overview of the folders and files, check out:")
    logger.info("   👉 project_structure.md")
    logger.info("It’ll help you understand how things are organized and where to start!")
    logger.info("Visit: https://github.com/pancht/nrobo/wiki/Getting-Started-with-nRobo")
