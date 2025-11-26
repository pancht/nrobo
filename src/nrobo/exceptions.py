class SuiteNotFoundError(FileNotFoundError):
    """Raised when the specified test suite YAML file cannot be found or loaded."""  # noqa: E501

    def __init__(self, suite_path: str):
        message = f"❌ Suite not found: {suite_path}"
        super().__init__(message)
        self.suite_path = suite_path
