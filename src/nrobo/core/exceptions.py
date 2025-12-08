from pathlib import Path

from nrobo.core.constants import ExitCodes


class NRoboError(Exception):
    """Base class for all nRoBo-related exceptions."""

    return_code: int = ExitCodes.INTERNAL_ERROR  # Default non-zero (generic failure)

    def __init__(self, message: str, return_code: int | None = None):
        super().__init__(message)
        if return_code is not None:
            self.return_code = return_code


class SuiteNotFoundError(NRoboError, FileNotFoundError):
    """Raised when the specified suite YAML file cannot be found."""

    return_code = ExitCodes.SUITE_NOT_FOUND

    def __init__(self, suite_path: Path):
        self.suite_path = suite_path
        message = f"❌ Suite not found: {suite_path}"
        super().__init__(message)


class ReadSuiteFailed(NRoboError):
    """Raised when reading or parsing a suite file fails."""

    return_code = ExitCodes.READ_SUITE_FAILED

    def __init__(self, suite_path: Path, reason: str | Exception | None = None):
        self.suite_path = suite_path
        self.reason = reason
        msg = f"⚠️ Failed to read suite: {suite_path}"
        if reason:
            msg += f"\n   → Reason: {reason}"
        super().__init__(msg)


class DependencyNotFoundError(NRoboError):
    """Raised when a required CLI or system dependency is not available."""

    return_code = ExitCodes.DEP_NOT_FOUND

    def __init__(self, dependency: str, install_hint: str | None = None):
        self.dependency = dependency
        self.install_hint = install_hint
        message = f"❌ Required dependency/CLI not found: {dependency}"
        if install_hint:
            message += f"\n   💡 To fix: {install_hint}"
        super().__init__(message)


class NoTestsFoundException(NRoboError):
    """Raised when no test suites or pytest tests are found."""

    return_code = ExitCodes.NO_TESTS_FOUND

    def __init__(self, reason: str | None = None, search_path: str | Path | None = None):
        self.reason = reason or "No test suites or pytest test files were detected."
        self.search_path = Path(search_path) if search_path else None

        message = f"❌ {self.reason}"
        if self.search_path:
            message += f"\n   🔍 Searched in: {self.search_path}"

        super().__init__(message)


class NoSubCommandFoundByArgParser(NRoboError):
    """Raised when no valid subcommand is found by CLI parser."""

    pass
