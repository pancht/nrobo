import os

def standardize_reoprt_path(report_type: str, report_dir:str, args: list):
    for i, arg in enumerate(args):
        if arg.startswith(f"--{report_type}="):
            path = arg.split("=", 1)[1]  # e.g. "report3/report.html"
            file_name = os.path.basename(path)  # -> "report.html"
            new_path = os.path.join(report_dir, file_name)  # -> "reports/report.html"
            args[i] = f"--{report_type}={new_path}"  # replace element
            break
    return  args


def standardize_html_reoprt_path(args: list):
    return standardize_reoprt_path(report_type="html", report_dir="reports", args=args)


def standardize_allure_reoprt_path(args: list):
    return standardize_reoprt_path(report_type="alluredir", report_dir="allure-results", args=args)
