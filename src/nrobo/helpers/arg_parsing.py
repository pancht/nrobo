import os


def standardize_html_reoprt_path(args: list):
    for i, arg in enumerate(args):
        if arg.startswith("--html="):
            path = arg.split("=", 1)[1]  # e.g. "report3/report.html"
            file_name = os.path.basename(path)  # -> "report.html"
            new_path = os.path.join("reports", file_name)  # -> "reports/report.html"
            args[i] = f"--html={new_path}"  # replace element
            break
    return  args

