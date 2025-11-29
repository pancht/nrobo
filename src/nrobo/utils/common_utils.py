import re
import secrets
import time


def deduplicate_preserve_order(items: list[str]) -> list[str]:
    """
    Remove duplicate strings from a list while preserving the original order.

    Example:
        >>> deduplicate_preserve_order(["smoke", "regression", "smoke"])
        ['smoke', 'regression']
    """
    if not items:
        return []
    return list(dict.fromkeys(items))


def generate_custom_id():
    timestamp = int(time.time() * 1000)
    random_part = secrets.token_hex(4)
    return f"id_{timestamp}_{random_part}"


def normalize_cli_output(output: str) -> str:
    """
    Normalize CLI output by cleaning up formatting artifacts and inconsistencies.

    Steps (in this exact order):
    1. Collapse multiple spaces into one
    2. Normalize line endings (Windows \r\n → Unix \n)
    3. Remove ANSI color codes (e.g. \x1b[31m for red)
    4. Replace multiple tabs with a single space
    5. Fix line breaks after hyphens (e.g. 'space-\n  separated' → 'space-separated')
    6. Remove all remaining newline characters (flatten into one line)
    """

    # Step 1: Collapse multiple spaces into one
    output = re.sub(r" {2,}", " ", output)

    # Step 2: Normalize CRLF (Windows) to LF (Unix)
    output = output.replace("\r\n", "\n")

    # Step 3: Remove ANSI escape sequences (like \x1b[31m)
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    output = ansi_escape.sub("", output)

    # Step 4: Replace multiple tabs with a single space
    output = re.sub(r"\t+", " ", output)

    # Step 5: Fix line breaks at hyphens (e.g. space-\n  separated → space-separated)
    output = re.sub(r"(?m)-\n\s*", "-", output)

    # Step 6: Remove all newlines (flatten output)
    output = output.replace("\n", "")

    return output
