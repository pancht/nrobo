from pathlib import Path


class NRoboError(Exception):
    """Base class for all nRoBo-related exceptions."""

    pass


class SuiteNotFoundError(NRoboError, FileNotFoundError):
    """Raised when the specified suite YAML file cannot be found."""

    def __init__(self, suite_path: Path):
        self.suite_path = suite_path
        message = f"❌ Suite not found: {suite_path}"
        super().__init__(message)


class ReadSuiteFailed(NRoboError):
    """Raised when reading or parsing a suite file fails."""

    def __init__(self, suite_path: Path, reason: str | Exception | None = None):  # noqa: E501
        self.suite_path = suite_path
        self.reason = reason
        msg = f"⚠️ Failed to read suite: {suite_path}"
        if reason:
            msg += f"\n   → Reason: {reason}"
        super().__init__(msg)
