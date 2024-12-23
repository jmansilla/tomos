from lark.lexer import Token

from tomos.ayed2.ast.base import ASTNode
from tomos.ayed2.ast.types import *


class Expr(ASTNode):
    pass


class _Literal(Expr):
    def __init__(self, token):
        assert isinstance(token, Token)
        self.token = token

    @property
    def value_str(self):
        return self.token.value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.value_str})"


class BooleanLiteral(_Literal):
    _type = BoolType


class IntegerLiteral(_Literal):
    _type = IntType


class RealLiteral(_Literal):
    _type = RealType


class CharLiteral(_Literal):
    _type = CharType


class NullLiteral(_Literal):
    _type = None


class EnumLiteral(_Literal):
    _type = None


class TraverseStep:
    DEREFERENCE = '*'
    ARRAY_INDEXING = '[%s]'
    ACCESSED_FIELD = '.%s'

    def __init__(self, kind, argument=None):
        assert kind in [TraverseStep.DEREFERENCE, TraverseStep.ARRAY_INDEXING, TraverseStep.ACCESSED_FIELD]
        self.kind = kind
        if kind is not TraverseStep.DEREFERENCE:
            assert argument is not None
        self.argument = argument


class Variable(Expr):
    DEREFERENCE = TraverseStep.DEREFERENCE
    ARRAY_INDEXING = TraverseStep.ARRAY_INDEXING
    ACCESSED_FIELD = TraverseStep.ACCESSED_FIELD

    def __init__(self, name_token):
        assert isinstance(name_token, Token)
        self.name_token = name_token
        self.traverse_path = []

    def traverse_append(self, kind, argument=None):
        step = TraverseStep(kind, argument)
        self.traverse_path.append(step)

    @property
    def name(self):
        return self.name_token.value

    @property
    def line_number(self):
        return self.name_token.line

    @property
    def symbols_name(self):
        star = "*" if self.dereferenced else ""
        return f"{star}{self.name}"

    def __str__(self):
        indexing = ""
        if self.array_indexing is not None:
            indexing = [str(i) for i in self.array_indexing]
        return f"{self.symbols_name}{indexing}"

    def __repr__(self) -> str:
        return f"Variable({str(self)})"

