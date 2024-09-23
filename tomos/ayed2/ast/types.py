#  Types
#  =====
#      ⟨type⟩ ::= int | real | bool | char
#               | ⟨array⟩
#               | ⟨pointer⟩
#               | ⟨defined_type⟩
#               | ⟨typevariable⟩
#
# [-]  ⟨array⟩ ::= array ⟨arraysize⟩ ... ⟨arraysize⟩ of ⟨type⟩
# [-]  ⟨arraysize⟩ ::= ⟨natural⟩ | ⟨sname⟩
#      ⟨pointer⟩ ::= pointer ⟨type⟩
#
# [-]  ⟨typevariable⟩ ::= ⟨typeid⟩
# [-]  ⟨defined_type⟩ ::= ⟨tname⟩ of ⟨type⟩ ... ⟨type⟩
#
# [-]  ⟨io⟩ ::= in | out | in/out
#
# [-]  ⟨class⟩ ::= Eq | Ord
#
# [-]  ⟨typedecl⟩ ::= enum ⟨tname⟩ = ⟨cname⟩ ... ⟨cname⟩
# [-]               | syn ⟨tname⟩ of ⟨typearguments⟩ = ⟨type⟩
# [-]               | tuple ⟨tname⟩ of ⟨typearguments⟩ = ⟨field⟩ ... ⟨field⟩
# [-]  ⟨typearguments⟩ ::= ⟨typevariable⟩ ... ⟨typevariable⟩
# [-]  ⟨field⟩ ::= ⟨fname⟩ : ⟨type⟩


class Ayed2TypeError(Exception):
    pass


class BasicType:
    def __init__(self, token):
        self._token = token

    def __repr__(self) -> str:
        return self.__class__.__name__


class IntType(BasicType):
    NAMED_CONSTANTS = {"inf": float("inf")}

    @classmethod
    def is_valid_value(cls, value):
        # dear python says that True and False are instances of int
        if isinstance(value, bool):
            return False
        return value in cls.NAMED_CONSTANTS.values() or isinstance(value, int)


class BoolType(BasicType):
    NAMED_CONSTANTS = {"true": True, "false": False}

    @classmethod
    def is_valid_value(cls, value):
        return isinstance(value, bool)


class RealType(BasicType):
    NAMED_CONSTANTS = {"inf": float("inf")}

    @classmethod
    def is_valid_value(cls, value):
        return value in cls.NAMED_CONSTANTS.values() or isinstance(value, float)


class CharType(BasicType):

    @classmethod
    def is_valid_value(cls, value):
        return isinstance(value, str) and len(value) == 1


class PointerOf(BasicType):
    NAMED_CONSTANTS = {"null": None}

    def __init__(self, token, of):
        super().__init__(token)
        self._of = of

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._of})"

    @classmethod
    def is_valid_value(cls, value):
        print('Needs to be implemented yet')
        # we'll need to deal with different pointer types
        return True


type_map = {
    "int": IntType,
    "real": RealType,
    "bool": BoolType,
    "char": CharType,
}
