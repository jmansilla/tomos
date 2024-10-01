class Ayed2TypeError(Exception):
    pass


class BasicType:

    def __repr__(self) -> str:
        return self.__class__.__name__


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


class ArrayOf(BasicType):
    def __init__(self, of, axes):
        assert all(isinstance(axis, ArrayAxis) for axis in axes)
        self.of = of
        self.axes = axes


class ArrayAxis:
    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value

    def __repr__(self):
        return f"Axis({self.from_value}, {self.to_value})"


type_map = {
    "int": IntType,
    "real": RealType,
    "bool": BoolType,
    "char": CharType,
}
