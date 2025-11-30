from pathlib import Path

from nrobo.core import settings


def test_nrobo_settings_default_constants_are_valid():
    """Ensure default settings paths are Path objects and resolve correctly."""

    configs_dir = "configs"
    env_file = ".env"
    assert settings.CONFIGS == configs_dir
    assert settings.ENV_FILE == env_file
    assert settings.DEV_ENV == settings.BASE_DIR.parent / configs_dir / env_file

    assert settings.NROBO_APP == "nRobo"
    assert isinstance(settings.NROBO_VERSION, str)
    assert isinstance(settings.BASE_DIR, Path), "BASE_DIR should be a Path"
    assert isinstance(settings.DEBUG, bool), "DEBUG should be a bool"
    assert isinstance(settings.DEFAULT_BROWSER, str)
    assert settings.DEFAULT_BROWSER == "chrome"
    assert settings.NROBO_BROWSER == "chrome"
    assert settings.NROBO_HEADLESS is True

    assert settings.REPORT_TYPE_HTML == "html"
    assert settings.HTML_REPORT_PATH == "reports"
    assert settings.HTML_DEFAULT_REPORT_NAME == "report.html"
    assert settings.REPORT_TYPE_ALLURE == "alluredir"
    assert settings.ALLURE_RESULTS_DIR == "allure-results"
    assert settings.ALLURE_REPORT_DIR == "allure-reports"

    assert settings.LOG_LEVEL_STREAM == "INFO"
    assert settings.LOG_FORMAT_STREAM == "%(log_color)s[%(levelname)s]%(reset)s %(message)s"
    assert settings.LOG_COLORS_STREAM == {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
    assert settings.LOG_FILE_FILE == ""
    assert settings.LOG_LEVEL_FILE == "DEBUG"
    assert settings.LOG_FORMAT_FILE == "%(asctime)s - %(levelname)s - %(message)s"

    assert settings.LOG_DIR == "logs"
    assert str(settings.SUITES_DIR) == "suites"
    assert str(settings.TESTS_DIR) == "tests"
    assert settings.UI_DIR == "ui"
    assert settings.MOBILE_DIR == "mobile"
    assert settings.API_DIR == "api"
    assert settings.PAGE_OBJECT_DIR == "pages"
    assert settings.TEST_DATA_DIR == "test_data"

    test_artifacts_dir = "test_artifacts"
    coverage_report_dir = "coverage_reports"
    assert settings.TEST_ARTIFACTS_DIR == test_artifacts_dir
    assert settings.COVERAGE_REPORTS_DIR == coverage_report_dir
    assert (
        settings.COVERAGE_REPORT_HTML
        == Path(test_artifacts_dir) / coverage_report_dir / "html" / "index.html"
    )
    assert (
        settings.COVERAGE_REPORT_XML
        == Path(test_artifacts_dir) / coverage_report_dir / "xml" / "coverage.xml"
    )
