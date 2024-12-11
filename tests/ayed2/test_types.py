from unittest import TestCase

from .factories.expressions import IntegerLiteralFactory
from .factories.state import StateFactory

from tomos.ayed2.ast.types import ArrayAxis, ArrayOf, IntType
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator
from tomos.exceptions import TomosTypeError


def _ArrayType(ranges_str):
    sep = ","
    ellipsis = ".."
    if not ranges_str.startswith("[") or not ranges_str.endswith("]"):
        raise ValueError
    ranges = ranges_str[1:-1].split(sep)
    axes = []
    for boundaries in ranges:
        if ellipsis not in boundaries:
            _from = IntegerLiteralFactory(token__value="0")
            _to = IntegerLiteralFactory(token__value=boundaries)
        else:
            _from_str, _to_str = boundaries.split(ellipsis)
            _from = IntegerLiteralFactory(token__value=_from_str)
            _to = IntegerLiteralFactory(token__value=_to_str)
        axes.append(ArrayAxis(_from, _to))

    return ArrayOf(IntType(), axes)


class TestArray(TestCase):
    def eval_expressions(self, _array):
        _array.eval_axes_expressions(ExpressionEvaluator(), StateFactory())
        return _array


class TestArraySizes(TestArray):

    def test_simple(self):
        at = self.eval_expressions(_ArrayType("[5]"))
        self.assertEqual(len(at.axes), 1)
        self.assertEqual(at.axes[0].from_value, 0)
        self.assertEqual(at.axes[0].to_value, 5)
        self.assertEqual(at.number_of_elements(), 5)

    def test_simple_with_ellipsis(self):
        at = self.eval_expressions(_ArrayType("[10..15]"))
        self.assertEqual(len(at.axes), 1)
        self.assertEqual(at.axes[0].from_value, 10)
        self.assertEqual(at.axes[0].to_value, 15)
        self.assertEqual(at.number_of_elements(), 5)

    def test_empty_range(self):
        at = self.eval_expressions(_ArrayType("[10..5]"))
        self.assertEqual(len(at.axes), 1)
        self.assertEqual(at.axes[0].from_value, 10)
        self.assertEqual(at.axes[0].to_value, 5)
        self.assertEqual(at.number_of_elements(), 0)

    def test_several_dimensions_simple(self):
        at = self.eval_expressions(_ArrayType("[5, 10, 8]"))
        self.assertEqual(len(at.axes), 3)
        self.assertEqual(at.axes[0].from_value, 0)
        self.assertEqual(at.axes[0].to_value, 5)
        self.assertEqual(at.axes[1].from_value, 0)
        self.assertEqual(at.axes[1].to_value, 10)
        self.assertEqual(at.axes[2].from_value, 0)
        self.assertEqual(at.axes[2].to_value, 8)
        self.assertEqual(at.number_of_elements(), 5 * 10 * 8)

    def test_several_dimensions_with_ellipsis(self):
        at = self.eval_expressions(_ArrayType("[5, 10..15, 8..12]"))
        self.assertEqual(len(at.axes), 3)
        self.assertEqual(at.axes[0].from_value, 0)
        self.assertEqual(at.axes[0].to_value, 5)
        self.assertEqual(at.axes[1].from_value, 10)
        self.assertEqual(at.axes[1].to_value, 15)
        self.assertEqual(at.axes[2].from_value, 8)
        self.assertEqual(at.axes[2].to_value, 12)
        self.assertEqual(at.number_of_elements(), 5 * (15-10) * (12-8))


class TestArrayIndexing(TestArray):

    def test_simple(self):
        at = self.eval_expressions(_ArrayType("[5]"))
        for i in range(5):
            idx = at.flatten_index([i])
            self.assertEqual(idx, i)

    def test_simple_with_ellipsis(self):
        at = self.eval_expressions(_ArrayType("[10..15]"))
        self.assertEqual(at.flatten_index([10]), 0)
        for i in range(10, 15):
            idx = at.flatten_index([i])
            self.assertEqual(idx, i-10)

    def test_several_dimensions_simple(self):
        at = self.eval_expressions(_ArrayType("[5, 10, 8]"))
        self.assertEqual(at.flatten_index([0, 0, 0]), 0)
        self.assertEqual(at.flatten_index([0, 0, 1]), 1)
        self.assertEqual(at.flatten_index([0, 1, 0]), 8)
        self.assertEqual(at.flatten_index([1, 0, 0]), 80)
        self.assertEqual(at.flatten_index([2, 3, 4]), 2 * 80 + 3 * 8 + 4)

    def test_out_of_range_raises(self):
        at = self.eval_expressions(_ArrayType("[5]"))
        with self.assertRaises(TomosTypeError):
            at.flatten_index([5])

    def test_wrong_range_raises(self):
        at = self.eval_expressions(_ArrayType("[5]"))
        with self.assertRaises(TomosTypeError):
            at.flatten_index([1, 2, 3])
        at = self.eval_expressions(_ArrayType("[5, 5]"))
        with self.assertRaises(TomosTypeError):
            at.flatten_index([1, 2, 3])
        with self.assertRaises(TomosTypeError):
            at.flatten_index([1])
