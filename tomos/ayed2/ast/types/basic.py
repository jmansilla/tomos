class Ayed2Type:
    is_pointer = False
    SIZE = None

    def __repr__(self) -> str:
        return self.__class__.__name__

    def is_valid_value(self, value):
        raise NotImplementedError()


class UserDefinedType(Ayed2Type):
    """Base class for user-defined types."""
    name = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.name}"


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
    SIZE = 1
    is_pointer = True

    def __init__(self, of):
        self.of = of

    def __repr__(self) -> str:
        return f"PointerOf({self.of})"

    @classmethod
    def is_valid_value(cls, value):
        from tomos.ayed2.evaluation.state import MemoryAddress  # FIXME
        return value in cls.NAMED_LITERALS.values() or isinstance(value, MemoryAddress)
