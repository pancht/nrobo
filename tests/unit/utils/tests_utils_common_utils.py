import re
import time

import pytest

from nrobo.utils.common_utils import (
    deduplicate_preserve_order,
    generate_custom_id,
    normalize_cli_output,
)


@pytest.mark.parametrize(
    "input_list, expected",
    [
        (["smoke", "regression", "smoke"], ["smoke", "regression"]),
        (["a", "b", "c", "a", "b"], ["a", "b", "c"]),
        (["only"], ["only"]),
        ([], []),
        (["x", "x", "x", "x"], ["x"]),
    ],
)
def test_deduplicate_preserve_order(input_list, expected):
    assert deduplicate_preserve_order(input_list) == expected


def test_generate_custom_id_format_and_prefix():
    custom_id = generate_custom_id()
    assert custom_id.startswith("id_")
    assert re.match(r"id_\d{13}_[a-f0-9]{8}", custom_id)


def test_generate_custom_id_is_unique():
    ids = {generate_custom_id() for _ in range(100)}
    assert len(ids) == 100  # No collisions


def test_generate_custom_id_timestamp_is_now():
    before = int(time.time() * 1000)
    generated_id = generate_custom_id()
    after = int(time.time() * 1000)

    timestamp = int(generated_id.split("_")[1])
    assert before <= timestamp <= after


@pytest.mark.parametrize(
    "raw_output, expected",
    [
        # Step 1: Collapse multiple spaces
        ("this  is   spaced", "this is spaced"),
        # Step 2: Normalize Windows line endings
        ("line1\r\nline2", "line1line2"),
        # Step 3: Remove ANSI escape sequences
        ("\x1b[31mred text\x1b[0m", "red text"),
        # Step 4: Replace multiple tabs with space
        ("col1\t\tcol2\tcol3", "col1 col2 col3"),
        # Step 5: Fix hyphen line breaks
        ("split-\n  word", "split-word"),
        # Step 6: Remove all newlines
        ("line1\nline2\nline3", "line1line2line3"),
        # Combo of all
        (
            "\x1b[32mFormatted  output\x1b[0m\r\nwith\t\tmany  spaces-\n  and lines\n",
            "Formatted outputwith many spaces-and lines",
        ),
    ],
)
def test_normalize_cli_output(raw_output, expected):
    assert normalize_cli_output(raw_output) == expected
