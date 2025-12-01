import os

from nrobo.core import settings


def standardize_reoprt_path(report_type: str, report_dir: str, args: list):
    for i, arg in enumerate(args):
        if (
            arg.startswith(f"--{settings.REPORT_TYPE_ALLURE}")
            and report_type == settings.REPORT_TYPE_ALLURE
        ):
            args[i + 1] = settings.ALLURE_RESULTS_DIR
            break  # no transformation needed

        if (
            arg.startswith(f"--{settings.REPORT_TYPE_HTML}=")
            and report_type == settings.REPORT_TYPE_HTML
        ):
            path = arg.split("=", 1)[1]  # e.g. "report3/report.html"
            file_name = os.path.basename(path)  # -> "report.html"
            new_path = os.path.join(report_dir, file_name)  # -> "reports/report.html" # noqa: E501
            args[i] = f"--{report_type}={new_path}"  # replace element
            break
    return args


def standardize_html_reoprt_path(args: list):
    return standardize_reoprt_path(
        report_type=settings.REPORT_TYPE_HTML,
        report_dir=settings.HTML_REPORT_PATH,
        args=args,  # noqa: E501
    )


def standardize_allure_reoprt_path(args: list):
    return standardize_reoprt_path(
        report_type=settings.REPORT_TYPE_ALLURE,
        report_dir=settings.ALLURE_RESULTS_DIR,
        args=args,  # noqa: E501
    )
