import math


class Ayed2TypeError(Exception):
    # TODO: rename to TomosTypeError, and move it to tomos module
    pass


class Ayed2Type:

    def __repr__(self) -> str:
        return self.__class__.__name__


class BasicType(Ayed2Type):
    pass


class IntType(BasicType):
    NAMED_LITERALS = {"inf": float("inf")}
    SIZE = 1

    @classmethod
    def is_valid_value(cls, value):
        # dear python says that True and False are instances of int
        if isinstance(value, bool):
            return False
        return value in cls.NAMED_LITERALS.values() or isinstance(value, int)


class BoolType(BasicType):
    NAMED_LITERALS = {"true": True, "false": False}
    SIZE = 1

    @classmethod
    def is_valid_value(cls, value):
        return isinstance(value, bool)


class RealType(BasicType):
    NAMED_LITERALS = {"inf": float("inf")}
    SIZE = 2

    @classmethod
    def is_valid_value(cls, value):
        return value in cls.NAMED_LITERALS.values() or isinstance(value, float)


class CharType(BasicType):
    NAMED_LITERALS = dict()
    SIZE = 1

    @classmethod
    def is_valid_value(cls, value):
        return isinstance(value, str) and len(value) == 1


class PointerOf(BasicType):
    NAMED_LITERALS = {"null": None}
    SIZE = 2

    def __init__(self, of):
        self.of = of

    def __repr__(self) -> str:
        return f"PointerOf({self.of})"

    @classmethod
    def is_valid_value(cls, value):
        from tomos.ayed2.evaluation.state import MemoryAddress
        return value in cls.NAMED_LITERALS.values() or isinstance(value, MemoryAddress)


class ArrayOf(Ayed2Type):
    def __init__(self, of, axes):
        assert all(isinstance(axis, ArrayAxis) for axis in axes)
        self.of = of
        self.axes = axes
        self._size = None

    def eval_axes_expressions(self, expr_evaluator, state):
        # In order to calculate the number of elements in an array,
        # and index-accessing, we need to know the number of elements
        # in each dimension (axis).
        # For such thing, we need to evaluate the expressions on axes
        for axis in self.axes:
            axis.eval_expressions(expr_evaluator, state)

    def number_of_elements(self):
        lengths = []
        for axis in self.axes:
            lengths.append(max(0, axis.to_value - axis.from_value))
        return math.prod(lengths)

    def element_size(self):
        if hasattr(self.of, 'SIZE'):
            return self.of.SIZE
        else:
            return self.of.element_size()

    def flatten_index(self, indexes):
        # If array is declated a[1..5, 10..15] and it's requested to access to position
        # a[4, 12], we need to decode that internally that's (in the flatten array) the
        # position a[3*5 + (12-10)] = a[3*5 + 2] = a[17]
        if len(indexes) != len(self.axes):
            raise Ayed2TypeError(f"Wrong number of indexes. Expected {len(self.axes)}, got {len(indexes)}")
        flatten_value = 0
        previous_size = 1
        for idx, axis in zip(reversed(indexes), reversed(self.axes)):
            if not axis.index_in_range(idx):
                raise Ayed2TypeError(f"Index {idx} is out of bounds for axis {axis}")
            flatten_value += (idx - axis.from_value) * previous_size
            previous_size *= axis.to_value - axis.from_value
        return flatten_value


class ArrayAxis:
    def __init__(self, from_expr, to_expr):
        self.from_expr = from_expr  # this is an expression, not a value
        self.to_expr = to_expr      # this is an expression, not a value

    def __repr__(self):
        return f"ArrayAxis({self.from_expr}, {self.to_expr})"

    def eval_expressions(self, expr_evaluator, state):
        self._cached_from_value = expr_evaluator.eval(self.from_expr, state)
        self._cached_to_value = expr_evaluator.eval(self.to_expr, state)

    def index_in_range(self, index):
        return self.from_value <= index < self.to_value

    @property
    def from_value(self):
        if not hasattr(self, "_cached_from_value"):
            raise Ayed2TypeError(f"Need to evaluate axis expressions first")
        return self._cached_from_value

    @property
    def to_value(self):
        if not hasattr(self, "_cached_to_value"):
            raise Ayed2TypeError(f"Need to evaluate axis expressions first")
        return self._cached_to_value


type_map = {
    "int": IntType,
    "real": RealType,
    "bool": BoolType,
    "char": CharType,
}
