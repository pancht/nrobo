import os
from pathlib import Path

from dotenv import load_dotenv

CONFIGS = "configs"
ENV_FILE = ".env"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEV_ENV = BASE_DIR.parent / CONFIGS / ENV_FILE
USR_ENV = BASE_DIR / CONFIGS / ENV_FILE
env_path = DEV_ENV if DEV_ENV.exists() else USR_ENV
load_dotenv(env_path)

# Core Framework Settings
NROBO_APP = os.getenv("NROBO_APP", "nRobo")
NROBO_VERSION = "0.1.0"

# Determine safe basetemp
safe_temp = os.getenv("NROBO_BASENAME_TMP", None)
NROBO_BASENAME_TMP = None if safe_temp is None else str(Path(safe_temp).absolute())

# APP Mode
DEBUG = os.getenv("NROBO_DEBUG", "False").lower() in ("true", "1", "yes")  # noqa: E501
# Test Execution
DEFAULT_BROWSER = os.getenv("NROBO_DEFAULT_BROWSER", "chrome")
NROBO_BROWSER = os.getenv("NROBO_BROWSER", "chrome")
NROBO_HEADLESS = os.getenv("NROBO_HEADLESS", "True").lower() in ("true", "1", "yes")  # noqa: E501

# Reporting
TEST_ARTIFACTS_DIR = "test_artifacts"
COVERAGE_REPORTS_DIR = "coverage_reports"
COVERAGE_REPORT_HTML = Path(TEST_ARTIFACTS_DIR) / COVERAGE_REPORTS_DIR / "html" / "index.html"
COVERAGE_REPORT_XML = Path(TEST_ARTIFACTS_DIR) / COVERAGE_REPORTS_DIR / "xml" / "coverage.xml"
REPORT_TYPE_HTML = os.getenv("NROBO_REPORT_TYPE_HTML", "html")
HTML_REPORT_PATH = str(
    Path(TEST_ARTIFACTS_DIR) / os.getenv("NROBO_HTML_REPORT_PATH", "html_report")
)
HTML_DEFAULT_REPORT_NAME = os.getenv("NROBO_HTML_DEFAULT_REPORT_NAME", "report.html")
REPORT_TYPE_ALLURE = os.getenv("NROBO_REPORT_TYPE_ALLURE", "alluredir")
ALLURE_RESULTS_DIR = str(
    Path(TEST_ARTIFACTS_DIR) / os.getenv("NROBO_ALLURE_RESULTS_DIR", "allure-results")
)
ALLURE_REPORT_DIR = str(
    Path(TEST_ARTIFACTS_DIR) / os.getenv("NROBO_ALLURE_REPORT_DIR", "allure-reports")
)
SCREENSHOTS = "screenshots"

# Logging Stream handler
LOG_LEVEL_STREAM = os.getenv("NROBO_LOG_LEVEL_STREAM", "INFO")
LOG_FORMAT_STREAM = os.getenv(
    "NROBO_LOG_FORMAT_STREAM", "%(log_color)s[%(levelname)s]%(reset)s %(message)s"
)
LOG_COLORS_STREAM = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

# Logging File Handler
LOG_FILE_FILE = os.getenv("NROBO_LOG_FILE_FILE", "")  # If set, use file logging
LOG_LEVEL_FILE = os.getenv("NROBO_LOG_LEVEL_FILE", "DEBUG")
LOG_FORMAT_FILE = os.getenv("NROBO_LOG_FORMAT_FILE", "%(asctime)s - %(levelname)s - %(message)s")

# standard directories
LOG_DIR = str(Path(TEST_ARTIFACTS_DIR) / os.getenv("NROBO_LOG_DIR", "logs"))
SUITES_DIR = Path(os.getenv("NROBO_SUITES_DIR", "test_suites"))
TESTS_DIR = Path(os.getenv("NROBO_TESTS_DIR", "tests"))
UI_DIR = os.getenv("NROBO_UI_DIR", "ui")
MOBILE_DIR = os.getenv("NROBO_MOBILE_DIR", "mobile")
API_DIR = os.getenv("NROBO_API_DIR", "api")
PAGE_OBJECT_DIR = os.getenv("NROBO_PAGE_OBJECT_DIR", "pages")
TEST_DATA_DIR = os.getenv("NROBO_TEST_DATA_DIR", "test_data")
