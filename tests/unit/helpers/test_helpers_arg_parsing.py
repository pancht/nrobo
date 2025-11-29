from unittest.mock import patch

from nrobo.helpers.arg_parsing import (
    standardize_allure_reoprt_path,
    standardize_html_reoprt_path,
    standardize_reoprt_path,
)


@patch("nrobo.core.settings.REPORT_TYPE_HTML", "html")
@patch("nrobo.core.settings.HTML_REPORT_PATH", "reports")
def test_standardize_html_report_path():
    args = ["--html=report3/repost4/report.html", "--color=yes"]
    result = standardize_html_reoprt_path(args.copy())
    assert result[0] == "--html=reports/report.html"
    assert result[1] == "--color=yes"


@patch("nrobo.core.settings.REPORT_TYPE_ALLURE", "alluredir")
@patch("nrobo.core.settings.ALLURE_RESULTS_DIR", "allure-results")
def test_standardize_allure_report_path():
    args = ["--alluredir", "tempasfds/rsss/eport.html", "--tb=short"]
    result = standardize_allure_reoprt_path(args.copy())
    assert result[0] == "--alluredir"
    assert result[1] == "allure-results"
    assert result[2] == "--tb=short"


def test_no_matching_arg_returns_same():
    args = ["--log-level=debug"]
    untouched = args.copy()
    output = standardize_reoprt_path("html-report", "some/dir", args)
    assert output == untouched
