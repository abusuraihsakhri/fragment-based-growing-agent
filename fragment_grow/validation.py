"""Shared CSV boolean parsing for both command-line interfaces."""

def parse_csv_bool(value):
    """Parse common explicit CSV booleans; reject ambiguous nonempty values."""
    if isinstance(value, bool):
        return value
    normalized = str(value if value is not None else "").strip().lower()
    if normalized in ("true", "1", "yes", "y", "t"):
        return True
    if normalized in ("false", "0", "no", "n", "f", ""):
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")
