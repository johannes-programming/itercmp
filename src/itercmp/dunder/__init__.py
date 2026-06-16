from collections.abc import Collection
from typing import Any

__all__ = ["ge", "gt", "le", "lt"]


def ge(x: Collection[Any], y: Collection[Any], /) -> Any:
    for a, b in zip(x, y):
        if a is b or a == b:
            continue
        return a >= b
    return len(x) >= len(y)


def gt(x: Collection[Any], y: Collection[Any], /) -> Any:
    for a, b in zip(x, y):
        if a is b or a == b:
            continue
        return a > b
    return len(x) > len(y)


def le(x: Collection[Any], y: Collection[Any], /) -> Any:
    for a, b in zip(x, y):
        if a is b or a == b:
            continue
        return a <= b
    return len(x) <= len(y)


def lt(x: Collection[Any], y: Collection[Any], /) -> Any:
    for a, b in zip(x, y):
        if a is b or a == b:
            continue
        return a < b
    return len(x) < len(y)
