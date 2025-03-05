import math

from tomos.exceptions import TomosTypeError
from .basic import Ayed2Type


class ArrayOf(Ayed2Type):
    def __init__(self, of, axes):
        assert all(isinstance(axis, ArrayAxis) for axis in axes)
        assert isinstance(of, Ayed2Type)
        self.of = of
        self.axes = axes
        self._size = None

    def __repr__(self) -> str:
        axes_str = [f"{x._from}..{x._to}" for x in self.axes]
        return f"ArrayOf({self.of}, [{', '.join(axes_str)}])"

    def eval_axes_expressions(self, expr_evaluator, state):
        # In order to calculate the number of elements in an array,
        # and index-accessing, we need to know the number of elements
        # in each dimension (axis).
        # For such thing, we need to evaluate the expressions on axes
        for axis in self.axes:
            axis.eval_expressions(expr_evaluator, state)

    def number_of_elements(self):
        return math.prod(self.shape())

    def shape(self):
        lengths = []
        for axis in self.axes:
            lengths.append(max(0, axis.to_value - axis.from_value))
        return lengths

    @property
    def SIZE(self):
        return self.number_of_elements() * self.element_size()  # type: ignore

    def is_valid_value(self, value):
        # In arrays, values are assigned to the elements of the array, not to
        # the array itself
        return self.of.is_valid_value(value)

    def element_size(self):
        if hasattr(self.of, "element_size"):
            return self.of.element_size()  # type: ignore
        else:
            return self.of.SIZE

    def flatten_index(self, indexes):
        # If array is declated a[1..5, 10..15] and it's requested to access to position
        # a[4, 12], we need to decode that internally that's (in the flatten array) the
        # position a[(4-1)*5 + (12-10)] = a[3*5 + 2] = a[17]
        if len(indexes) != len(self.axes):
            raise TomosTypeError(
                f"Wrong number of indexes. Expected {len(self.axes)}, got {len(indexes)}"
            )
        if not all(isinstance(idx, int) for idx in indexes):
            raise TomosTypeError(f"Expected integer indexes, got {indexes}")
        flatten_value = 0
        previous_size = 1
        for idx, axis in zip(reversed(indexes), reversed(self.axes)):
            if not axis.index_in_range(idx):
                raise TomosTypeError(f"Index {idx} is out of bounds for axis {axis}")
            flatten_value += (idx - axis.from_value) * previous_size
            previous_size *= axis.to_value - axis.from_value
        return flatten_value

    def has_deferrals(self, crumbs=[]):
        if self in crumbs:
            return False  # avoid infinite loop
        return self.of.has_deferrals(crumbs + [self])

    def resolve_deferrals(self, crumbs):
        if self.of.has_deferrals(crumbs + [self]):
            self.of.resolve_deferrals(crumbs + [self])
        return self


class ArrayAxis:

    class Limit:
        def __init__(self, data):
            from tomos.ayed2.ast.expressions import Expr  # avoid circular import

            if isinstance(data, int):
                self.value = data
            else:
                assert isinstance(data, Expr)
                self.expr = data

        def __repr__(self):
            if hasattr(self, "value"):
                return repr(self.value)
            return repr(self.expr)

        def eval(self, expr_evaluator, state):
            if hasattr(self, "value"):
                return
            self.value = expr_evaluator.eval(self.expr, state)

    def __init__(self, from_expr_or_val, to_expr):
        self._from = self.Limit(from_expr_or_val)
        self._to = self.Limit(to_expr)

    def __repr__(self):
        return f"ArrayAxis({self._from}, {self._to})"

    def eval_expressions(self, expr_evaluator, state):
        self._from.eval(expr_evaluator, state)
        self._to.eval(expr_evaluator, state)

    def index_in_range(self, index):
        return self.from_value <= index and index < self.to_value

    @property
    def from_value(self):
        if not hasattr(self._from, "value"):
            raise TomosTypeError("Need to evaluate axis expressions first")
        return self._from.value

    @property
    def to_value(self):
        if not hasattr(self._to, "value"):
            raise TomosTypeError("Need to evaluate axis expressions first")
        return self._to.value

    @property
    def length(self):
        if not hasattr(self._to, "value") or not hasattr(self._from, "value"):
            raise TomosTypeError("Need to evaluate axis expressions first")
        return self.to_value - self.from_value
