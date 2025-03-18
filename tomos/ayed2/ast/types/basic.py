class Ayed2Type:
    is_pointer = False
    is_deferred = False
    SIZE = None

    def __repr__(self) -> str:
        return self.__class__.__name__

    def is_valid_value(self, value):
        raise NotImplementedError()

    @staticmethod
    def has_deferrals(crumbs=[]):
        return False

    def resolve_deferrals(self, crumbs=[]):
        return self


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


class NullValue:
    def __repr__(self) -> str:
        return "null"

    def __hash__(self):
        return hash("NullValue instance")

    def __eq__(self, other):
        return isinstance(other, NullValue)


class PointerOf(BasicType):
    NAMED_LITERALS = {"null": NullValue()}
    SIZE = 1
    is_pointer = True

    def __init__(self, of):
        from .registry import type_registry  # avoid circular import

        assert isinstance(of, (Ayed2Type, type_registry.Deferred))
        self.of = of

    def __repr__(self) -> str:
        return f"PointerOf({self.of})"

    @classmethod
    def is_valid_value(cls, value):
        from tomos.ayed2.evaluation.state import MemoryAddress  # circular import
        return value in cls.NAMED_LITERALS.values() or isinstance(value, MemoryAddress)

    def has_deferrals(self, crumbs=[]):
        if self.of.is_deferred:
            return True
        elif self in crumbs:
            return False  # avoid infinite loop
        else:
            return self.of.has_deferrals(crumbs + [self])  # type: ignore

    def resolve_deferrals(self, crumbs=[]):
        if self.of.is_deferred:
            self.of = self.of.resolve()  # type: ignore
        elif self.of.has_deferrals(crumbs + [self]):  # type: ignore
            self.of.resolve_deferrals()  # type: ignore
        return self
