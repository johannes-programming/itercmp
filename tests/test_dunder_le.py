import unittest
from collections.abc import Generator
from typing import Any, Self

import itercmp.dunder

__all__ = ["TestDunderLe"]


class TestDunderLe(unittest.TestCase):
    def gen_000(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                return NotImplemented

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __ge__(self: Self, other: object, /) -> Any:
                return False

        yield (A(),), (B(),)

    def gen_001(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                return NotImplemented

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __ge__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (B(),)

    def gen_900(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                return 42

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

        yield (A(),), (B(),)

    def test_0_000(self: Self) -> None:
        gens: list[Any]
        t: type[Any]
        x: Any
        x_: Any
        y: Any
        y_: Any
        gens = [
            self.gen_000,
            self.gen_001,
            self.gen_900,
        ]
        for gen in gens:
            for x, y in gen():
                for t in (tuple, list):
                    x_ = t(x)
                    y_ = t(y)
                    self.assertEqual(itercmp.dunder.le(x_, y_), x_.__le__(y_))
