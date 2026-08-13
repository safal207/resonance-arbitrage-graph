from __future__ import annotations


def require_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
