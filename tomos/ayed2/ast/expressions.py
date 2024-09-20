#  Expressions
#  ===========
#      ⟨expression⟩ ::= ⟨constant⟩ | ⟨functioncall⟩ | ⟨operation⟩ | ⟨variable〉
#      ⟨constant⟩ ::= ⟨integer⟩ | ⟨real⟩ | ⟨bool⟩ | ⟨character⟩ | ⟨enum_name⟩ | inf | null
# [-]  ⟨functioncall⟩ ::= ⟨id⟩ ( ⟨expression⟩ ... ⟨expression⟩ )
#      ⟨operation⟩ ::= ⟨expression⟩ ⟨binary⟩ ⟨expression⟩ | ⟨unary⟩ ⟨expression⟩
#      ⟨binary⟩ ::= + | − | * | / | % | || | && | <= | >= | < | > | == | !=
#      ⟨unary⟩ ::= - | !
#      ⟨variable⟩ ::= ⟨id⟩
#                   | ⟨variable⟩[⟨expression⟩ ... ⟨expression⟩ ]
#                   | ⟨variable⟩.⟨fname⟩
#                   | *⟨variable⟩

from tomos.ayed2.ast.types import *


class Expr:
    pass


class _Constant(Expr):
    def __init__(self, token):
        self._token = token

    @property
    def value_str(self):
        return self._token.value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.value_str})"


class BooleanConstant(_Constant):
    type = BoolType


class IntegerConstant(_Constant):
    type = IntType


class RealConstant(_Constant):
    type = RealType


class Variable(Expr):
    def __init__(self, name):
        self._name_token = name

    @property
    def name(self):
        return self._name_token.value

    def __repr__(self) -> str:
        return f"Variable({self.name})"


class FunctionCall(Expr):
    def __init__(self, name, args):
        self._name_token = name
        self._args = args

    @property
    def name(self):
        return self._name_token.value

    @property
    def args(self):
        return self._args

    def __repr__(self) -> str:
        return f"FunctionCall({self.name}, {self.args})"
