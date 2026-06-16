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

    def gen_002(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Identity short-circuit: the SAME object in both positions must be
        # treated as equal even when __eq__ says otherwise (the nan case).
        # __le__ returns False so a missing `is` check would give the wrong
        # answer instead of falling through to the length comparison.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                return False

        a = A()
        yield (a,), (a,)  # identity -> equal -> 1 <= 1 -> True
        yield (a, 1), (a, 2)  # identity skips, then 1 <= 2 -> True
        yield (a, 2), (a, 1)  # identity skips, then 2 <= 1 -> False

    def gen_003(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Equal prefix -> result decided purely by length, every direction.
        yield (1, 2), (1, 2, 3)  # proper prefix, shorter  -> True
        yield (1, 2, 3), (1, 2)  # proper prefix, longer   -> False
        yield (1, 2), (1, 2)  # identical               -> True
        yield (), ()  # both empty              -> True
        yield (), (1,)  # empty vs non-empty      -> True
        yield (1,), ()  # non-empty vs empty      -> False

    def gen_004(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Only the first differing pair decides; trailing elements are ignored.
        yield (1, 9, 9), (2, 0, 0)  # 1 <= 2 -> True regardless of rest
        yield (2, 0, 0), (1, 9, 9)  # 2 <= 1 -> False regardless of rest
        yield (1, 5), (1, 4, 100)  # 5 <= 4 -> False even though lhs shorter

    def gen_005(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # __eq__ may return a non-bool; only its *truthiness* counts.
        class Truthy:
            def __eq__(self: Self, other: object, /) -> Any:
                return "non-empty"  # truthy -> treated as equal

            def __le__(self: Self, other: object, /) -> Any:
                return False  # must NOT be reached

        class Falsy:
            def __eq__(self: Self, other: object, /) -> Any:
                return []  # falsy -> treated as different

            def __le__(self: Self, other: object, /) -> Any:
                return True

        yield (Truthy(),), (Truthy(),)  # equal -> 1 <= 1 -> True
        yield (Falsy(),), (Falsy(),)  # differ -> __le__ -> True

    def gen_006(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Reflected fallback: __le__ is absent, so a <= b uses b.__ge__(a).
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __ge__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (B(),)  # A() <= B() -> B().__ge__(A()) -> True

    def gen_007(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Cross-type numeric elements compared element-wise.
        yield (1, 2.0), (1.0, 2)  # all equal -> 2 <= 2 -> True
        yield (True, 0), (1, False)  # bool/int equality -> True
        yield (1,), (1.5,)  # 1 <= 1.5 -> True

    def gen_008(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Strings and nested sequences: the differing element uses its own <=.
        yield ("a", "b"), ("a", "c")
        yield ("abc",), ("abd",)
        yield ((1, 2),), ((1, 3),)
        yield ((1, 2), 9), ((1, 2), 8)

    def gen_009(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # The motivating real-world case: nan.
        nan = float("nan")
        yield (nan,), (nan,)  # same obj -> True
        yield (float("nan"),), (float("nan"),)  # distinct -> nan<=nan -> False
        yield (1, nan), (1, nan)  # same obj after equal prefix
        yield (1, float("nan")), (
            1,
            float("nan"),
        )  # distinct after equal prefix

    def gen_010(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Both directions NotImplemented -> a <= b raises TypeError; the
        # container __le__ must propagate it identically.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                return NotImplemented

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __ge__(self: Self, other: object, /) -> Any:
                return NotImplemented

        yield (A(),), (B(),)

    def gen_011(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # __eq__ raises during the equality scan. The exception must propagate
        # identically (type, repr, str) instead of being swallowed. Distinct
        # objects, so the identity short-circuit does not hide the call.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                raise ValueError("eq boom")

            def __le__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (A(),)
        yield (1, A()), (1, A())  # raise only after an equal prefix

    def gen_012(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # First pair is unequal, so the FINAL element comparison is reached and
        # its __le__ raises -> must propagate identically.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                raise RuntimeError("le boom")

        yield (A(),), (A(),)

    def gen_013(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # __eq__ returns an object whose __bool__ raises (the numpy-array
        # "ambiguous truth value" case). Taking truthiness of the eq result
        # must raise the same way PyObject_IsTrue does at the C level.
        class Ambiguous:
            def __bool__(self: Self, /) -> Any:
                raise ValueError("ambiguous truth value")

        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return Ambiguous()

            def __le__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (A(),)

    def gen_014(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Both sides' __eq__ return NotImplemented -> Python falls back to
        # identity (False for distinct objects) -> the pair counts as DIFFERENT
        # and the element __le__ decides. An unresolved __eq__ must not be
        # mistaken for "equal".
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

            def __le__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (A(),)

    def gen_015(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Identity short-circuit must skip a __eq__ that would otherwise raise,
        # proving `is` is tested BEFORE `==`. Same object at the first and at a
        # middle position.
        class Boom:
            def __eq__(self: Self, other: object, /) -> Any:
                raise ValueError("must not be called")

            def __le__(self: Self, other: object, /) -> Any:
                return False

        b = Boom()
        yield (b,), (b,)  # identity at pos 0 -> 1 <= 1 -> True
        yield (1, b, 2), (1, b, 3)  # identity mid, then 2 <= 3 -> True
        yield (1, b, 9), (1, b, 8)  # identity mid, then 9 <= 8 -> False

    def gen_016(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Neither __le__ nor __ge__ defined; __lt__ is present as a red herring
        # (<= must NOT consult it) -> a <= b raises TypeError. Confirms the
        # identical "not supported between instances" message on both paths.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __lt__(self: Self, other: object, /) -> Any:
                return True

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

        yield (A(),), (B(),)

    def gen_017(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Long genuinely-equal prefix, divergence only at the last element.
        yield (1, 2, 3, 4, 5), (1, 2, 3, 4, 6)
        yield (1, 2, 3, 4, 6), (1, 2, 3, 4, 5)
        yield (1, 2, 3, 4, 5), (1, 2, 3, 4, 5)

    def gen_018(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Nested sequences whose own <= / length comparison decides the result.
        yield ((1, 2),), ((1, 2, 3),)  # inner: proper prefix  -> True
        yield ((1, 2, 3),), ((1, 2),)  # inner: longer         -> False
        yield ((1, 2), (3,)), ((1, 2), (3, 0))

    def gen_019(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Reflected fallback returning a NON-bool object must be preserved
        # verbatim (the gen_900 idea, but reached through b.__ge__).
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __ge__(self: Self, other: object, /) -> Any:
                return "reflected-yes"

        yield (A(),), (B(),)

    def gen_020(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # __eq__ truthiness resolved via __len__ rather than __bool__: empty
        # result -> falsy -> different; non-empty -> truthy -> equal.
        class WithLen:
            def __init__(self: Self, n: int, /) -> None:
                self.n = n

            def __len__(self: Self, /) -> int:
                return self.n

        class Eq0:
            def __eq__(self: Self, other: object, /) -> Any:
                return WithLen(0)  # falsy -> treated as different

            def __le__(self: Self, other: object, /) -> Any:
                return True

        class Eq1:
            def __eq__(self: Self, other: object, /) -> Any:
                return WithLen(1)  # truthy -> treated as equal

            def __le__(self: Self, other: object, /) -> Any:
                return False  # must NOT be reached

        yield (Eq0(),), (Eq0(),)  # differ -> __le__ -> True
        yield (Eq1(),), (Eq1(),)  # equal  -> 1 <= 1 -> True

    def gen_021(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Reflected fallback itself raises: a.__le__ defers (NotImplemented),
        # then b.__ge__ raises -> exception propagates from the element compare.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __le__(self: Self, other: object, /) -> Any:
                return NotImplemented

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

            def __ge__(self: Self, other: object, /) -> Any:
                raise RuntimeError("ge boom")

        yield (A(),), (B(),)

    def gen_022(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Identity short-circuit AFTER a real (==, not identity) equal prefix,
        # combined with a distinct-nan tail; exercises is / == / length together.
        nan = float("nan")
        marker = object()
        yield (1, marker, nan), (1, marker, nan)  # same nan object -> True
        yield (1, marker), (1, marker, 0)  # equal prefix -> length -> True

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

    def gen_901(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

            def __le__(self: Self, other: object, /) -> Any:
                return True

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (B(),)

    def gen_902(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

            def __le__(self: Self, other: object, /) -> Any:
                return True

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

        yield (A(),), (B(),)

    def gen_903(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

            def __le__(self: Self, other: object, /) -> Any:
                return False

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (B(),)

    def gen_904(self: Self) -> Generator[tuple[Any, Any], None, None]:
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

            def __le__(self: Self, other: object, /) -> Any:
                return False

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return False

        yield (A(),), (B(),)

    def gen_905(self: Self) -> Generator[tuple[Any, Any], None, None]:
        # Both __eq__ return NotImplemented (distinct objects) -> equality falls
        # back to identity (False) -> different -> a <= b via reflected __ge__.
        class A:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

        class B:
            def __eq__(self: Self, other: object, /) -> Any:
                return NotImplemented

            def __ge__(self: Self, other: object, /) -> Any:
                return True

        yield (A(),), (B(),)

    def go(self: Self, c: Any, x: Any, y: Any, /) -> tuple[Any, Any]:
        try:
            return c(x, y), None
        except Exception as exc:
            return None, exc

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
            self.gen_002,
            self.gen_003,
            self.gen_004,
            self.gen_005,
            self.gen_006,
            self.gen_007,
            self.gen_008,
            self.gen_009,
            self.gen_010,
            self.gen_011,
            self.gen_012,
            self.gen_013,
            self.gen_014,
            self.gen_015,
            self.gen_016,
            self.gen_017,
            self.gen_018,
            self.gen_019,
            self.gen_020,
            self.gen_021,
            self.gen_022,
            self.gen_900,
            self.gen_901,
            self.gen_902,
            self.gen_903,
            self.gen_904,
            self.gen_905,
        ]
        for gen in gens:
            for x, y in gen():
                for t in (tuple, list):
                    x_ = t(x)
                    y_ = t(y)
                    ans_old, exc_old = self.go(t.__le__, x_, y_)
                    ans_new, exc_new = self.go(itercmp.dunder.le, x_, y_)
                    self.assertEqual(ans_old, ans_new)
                    self.assertEqual(repr(exc_old), repr(exc_new))
                    self.assertEqual(str(exc_old), str(exc_new))
                    self.assertIs(type(exc_old), type(exc_new))
