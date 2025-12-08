class ExitCodes:
    SUCCESS = 0
    SUITE_NOT_FOUND = 201
    READ_SUITE_FAILED = 202
    DEP_NOT_FOUND = 203
    NO_TESTS_FOUND = 204
    NO_SUBCOMMAND_IN_ARGS = 205
    INTERRUPTED = 130  # KeyboardInterrupt
    INTERNAL_ERROR = 99  # Generic unhandled exception


pytest_non_execution_keys = [
    "--collect-only",
    "--co",
    "--fixtures",
    "--fixtures-per-test",
    "--markers",
    "--help",
    "--version",
    "--trace-config",
    "--setup-plan",
    "--setup-only",
    "--setup-show",
    "--confcutdir",  # "--confcutdir=DIR",
]
