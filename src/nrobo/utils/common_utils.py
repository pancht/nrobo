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
