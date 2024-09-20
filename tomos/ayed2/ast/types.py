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
    pass


class BoolType(BasicType):
    pass


class RealType(BasicType):
    pass


class CharType(BasicType):
    pass


class PointerOf(BasicType):
    def __init__(self, token, of):
        super().__init__(token)
        self._of = of

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._of})"


type_map = {
    "int": IntType,
    "real": RealType,
    "bool": BoolType,
    "char": CharType,
}
