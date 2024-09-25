#  Expressions
#  ===========
#      ⟨expression⟩ ::= ⟨constant⟩ | ⟨functioncall⟩ | ⟨operation⟩ | ⟨variable〉
#      ⟨constant⟩ ::= ⟨integer⟩ | ⟨real⟩ | ⟨bool⟩ | inf | null
# [-]                 | ⟨character⟩ | ⟨enum_name⟩
# [-]  ⟨functioncall⟩ ::= ⟨id⟩ ( ⟨expression⟩ ... ⟨expression⟩ )
#      ⟨operation⟩ ::= ⟨expression⟩ ⟨binary⟩ ⟨expression⟩ | ⟨unary⟩ ⟨expression⟩
#      ⟨binary⟩ ::= + | − | * | / | % | || | && | <= | >= | < | > | == | !=
#      ⟨unary⟩ ::= - | !
#      ⟨variable⟩ ::= ⟨id⟩
# [-]               | ⟨variable⟩[⟨expression⟩ ... ⟨expression⟩ ]
# [-]               | ⟨variable⟩.⟨fname⟩
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
    _type = BoolType


class IntegerConstant(_Constant):
    _type = IntType


class RealConstant(_Constant):
    _type = RealType


class CharConstant(_Constant):
    _type = CharType


class Variable(Expr):
    def __init__(self, name, address_of=False, dereferenced=False):
        self._name_token = name
        self._address_of = address_of
        self._dereferenced = dereferenced

    @property
    def name(self):
        return self._name_token.value

    @property
    def line_number(self):
        return self._name_token.line

    @property
    def symbols_name(self):
        address = "&" if self._address_of else ""
        star = "*" if self._dereferenced else ""
        return f"{address}{star}{self.name}"

    def __repr__(self) -> str:
        return f"Variable({self.symbols_name})"


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
