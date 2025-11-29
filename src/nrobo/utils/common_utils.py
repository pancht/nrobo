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
    return f"id-{timestamp}-{random_part}"
