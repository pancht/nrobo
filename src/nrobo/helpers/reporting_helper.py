import subprocess  # nosec B404
from pathlib import Path

from nrobo.core import settings
from nrobo.core.exceptions import DependencyNotFoundError
from nrobo.helpers.arg_parsing import (
    standardize_allure_reoprt_path,
    standardize_html_reoprt_path,
)
from nrobo.helpers.logging_helper import get_logger
from nrobo.services.nginx_service import reuse_or_launch_allure_nginx

logger = get_logger(name=settings.NROBO_APP)


def check_dependency(name: str, install_hint: str | None = None):
    import shutil

    if shutil.which(name) is None:
        raise DependencyNotFoundError(name, install_hint)


def prepare_reporting_args(pytest_args: list[str]) -> list[str]:
    """
    Ensure pytest command-line args include valid HTML and Allure reporting options. # noqa: E501

    - Normalizes user-provided report paths
    - Adds defaults if missing
    """
    # ✅ HTML report handling
    if any("--html" in arg for arg in pytest_args):
        pytest_args = standardize_html_reoprt_path(pytest_args)
    else:
        pytest_args.extend(
            [
                f"--{settings.REPORT_TYPE_HTML}={settings.HTML_REPORT_PATH}/{settings.HTML_DEFAULT_REPORT_NAME}",  # noqa: E501
                "--self-contained-html",
            ]
        )

    # ✅ Allure report handling
    if any(f"--{settings.REPORT_TYPE_ALLURE}" in arg for arg in pytest_args):
        pytest_args = standardize_allure_reoprt_path(pytest_args)
    else:
        pytest_args.extend(["--alluredir", settings.ALLURE_RESULTS_DIR])

    return pytest_args


def generate_allure_report() -> None:
    """
    Generates the Allure HTML report from results directory.
    Ensures allure CLI is available before running.
    """
    check_dependency(
        name="allure",
        install_hint="Visit https://allurereport.org/docs/install/ for setup instructions.",  # noqa: E501
    )

    try:
        subprocess.run(  # nosec B603
            [
                "allure",
                "generate",
                settings.ALLURE_RESULTS_DIR,
                "-o",
                settings.ALLURE_REPORT_DIR,
                "--clean",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        report_path = Path(settings.ALLURE_REPORT_DIR).resolve() / "index.html"
        logger.info(f"✅ Allure report ready  →  file://{report_path}")
        try:
            state = reuse_or_launch_allure_nginx(settings.ALLURE_REPORT_DIR, open_browser=False)
            logger.info(f"Allure report served at url: {state['url']}")
        except Exception as e:  # pragma: no cover
            logger.debug(e)  # pragma: no cover
    except subprocess.CalledProcessError as e:
        logger.error("❌ Failed to generate Allure report.")
        logger.error(f"Command: {e.cmd}")
        logger.error(f"Exit Code: {e.returncode}")
        logger.error(f"Output: {e.output}")
        logger.error(f"Error Output: {e.stderr}")
