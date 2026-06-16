import operator as op
from collections.abc import Callable, Collection
from functools import partial
from typing import Any

__all__ = ["ge", "gt", "le", "lt", "ordering"]

# def eq(x: Collection[Any], y: Collection[Any], /) -> bool:
#    for a, b in zip(x, y):
#        if a is b or a == b:
#            continue
#        return False
#    return len(x) == len(y)


def ordering(
    operator: Callable[[Any, Any], Any],
    x: Collection[Any],
    y: Collection[Any],
    /,
) -> Any:
    for a, b in zip(x, y):
        if a is b or a == b:
            continue
        return operator(x, y)
    return operator(len(x), len(y))


ge = partial(ordering, op.ge)
gt = partial(ordering, op.gt)
le = partial(ordering, op.le)
lt = partial(ordering, op.lt)
