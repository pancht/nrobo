from pathlib import Path
from typing import List, Optional, Union

import yaml

from nrobo.core import settings
from nrobo.core.exceptions import ReadSuiteFailed, SuiteNotFoundError
from nrobo.helpers.logging_helper import get_logger

logger = get_logger(settings.NROBO_APP)

#
# def prepare_pytest_cli_options(
#     suites: Optional[Union[str, List[str]]] = None,
#     pytest_args: Optional[List[str]] = None,
#     test_dir: Optional[Path] = None,
#     suite_dir: Optional[Path] = None,
# ) -> List[str]:
#     """
#     Build the final list of pytest CLI options based on suite YAML files and extra args.
#
#     Args:
#         suites: Single suite file name, list of suite files, or None.
#         pytest_args: Additional pytest command-line arguments.
#         test_dir: Optional path override for tests dir (used for testing).
#         suite_dir: Optional path override for suites dir (used for testing).
#
#     Returns:
#         List of pytest CLI arguments to pass to pytest.main().
#     """
#     test_dir = Path(test_dir or Path.cwd() / settings.TESTS_DIR)
#     suite_dir = Path(suite_dir or Path.cwd() / settings.SUITES_DIR)
#
#     selected_tests = [str(test_dir)]
#
#     if suites:
#         selected_tests = []
#         suite_files = [suites] if isinstance(suites, str) else suites
#
#         for suite_file in suite_files:
#             suite_path = suite_dir / suite_file
#             if not suite_path.exists():
#                 raise SuiteNotFoundError(suite_path=suite_path)
#
#             try:
#                 with suite_path.open(encoding="utf-8") as f:
#                     suite_data = yaml.safe_load(f) or {}
#             except Exception as e:
#                 raise ReadSuiteFailed(suite_path=suite_path, reason=e)
#
#             for test_name in suite_data.get("tests", []):
#                 selected_tests.append(str(test_dir / test_name))
#
#     selected_tests = selected_tests or [str(test_dir)]
#     return (pytest_args or []) + selected_tests
