import os
from pathlib import Path

# Core Framework Settings
APP = "nRobo"
NROBO_VERSION = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# APP Mode
DEBUG = os.getenv("NROBO_DEBUG", "False").lower() in ("true", "1", "yes")  # noqa: E501
# Test Execution
DEFAULT_BROWSER = "chrome"
NROBO_BROWSER = os.getenv("NROBO_BROWSER", "chrome")
NROBO_HEADLESS = os.getenv("NROBO_HEADLESS", "True").lower() in ("true", "1", "yes")  # noqa: E501

# Reporting
REPORT_TYPE_HTML = "html"
HTML_REPORT_PATH = "reports"
HTML_DEFAULT_REPORT_NAME = "report.html"
REPORT_TYPE_ALLURE = "alluredir"
ALLURE_RESULTS_DIR = "allure-results"
ALLURE_REPORT_DIR = "allure-reports"

# Logging Stream handler
LOG_LEVEL_STREAM = os.getenv("NROBO_LOG_LEVEL", "INFO")
LOG_FORMAT_STREAM = "%(log_color)s[%(levelname)s]%(reset)s %(message)s"
LOG_COLORS_STREAM = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}
# Logging File Handler
LOG_FILE_FILE = os.getenv("NROBO_LOG_FILE", "")  # If set, use file logging
LOG_LEVEL_FILE = os.getenv("NROBO_LOG_LEVEL", "DEBUG")
LOG_FORMAT_FILE = "%(asctime)s - %(levelname)s - %(message)s"

# standard directories
LOG_DIR = "logs"
SUITES_DIR = "suites"
TESTS_DIR = "tests"
UI_DIR = "ui"
MOBILE_DIR = "mobile"
API_DIR = "api"
PAGE_OBJECT_DIR = "pages"
TEST_DATA_DIR = "test_data"
