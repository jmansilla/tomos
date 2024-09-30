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

from lark.lexer import Token
from tomos.ayed2.ast.types import *


class Expr:

    @property
    def line_number(self):
        raise NotImplementedError


class _Constant(Expr):
    def __init__(self, token):
        assert isinstance(token, Token)
        self.token = token

    @property
    def value_str(self):
        return self.token.value

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


class NullConstant(_Constant):
    _type = None


class Variable(Expr):
    def __init__(self, name_token, address_of=False, dereferenced=False):
        self.name_token = name_token
        self.address_of = address_of
        self.dereferenced = dereferenced

    @property
    def name(self):
        return self.name_token.value

    @property
    def line_number(self):
        return self.name_token.line

    @property
    def symbols_name(self):
        address = "&" if self.address_of else ""
        star = "*" if self.dereferenced else ""
        return f"{address}{star}{self.name}"

    def __repr__(self) -> str:
        return f"Variable({self.symbols_name})"
