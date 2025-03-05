from tomos.ayed2.ast.base import ASTNode
from tomos.ayed2.ast.types import *
from tomos.ayed2.parser.token import Token


class Expr(ASTNode):
    is_lazy = False


class LazyExpr(Expr):
    is_lazy = True

    def __init__(self, expr):
        assert isinstance(expr, Expr)
        self.expr = expr

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.expr})"

    @property
    def line_number(self):
        return self.expr.line_number


class _Literal(Expr):
    def __init__(self, token):
        assert isinstance(token, Token)
        self.token = token

    @property
    def value_str(self):
        return self.token.value

    @property
    def line_number(self):
        return self.token.line

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
    DEREFERENCE = "*"
    ARRAY_INDEXING = "[%s]"
    ACCESSED_FIELD = ".%s"

    def __init__(self, kind, argument=None):
        assert kind in [
            TraverseStep.DEREFERENCE,
            TraverseStep.ARRAY_INDEXING,
            TraverseStep.ACCESSED_FIELD,
        ]
        self.kind = kind
        if kind is not TraverseStep.DEREFERENCE:
            assert argument is not None
        if kind is TraverseStep.ARRAY_INDEXING:
            assert isinstance(argument, list)
        self.argument = argument


class Variable(Expr):
    DEREFERENCE = TraverseStep.DEREFERENCE
    ARRAY_INDEXING = TraverseStep.ARRAY_INDEXING
    ACCESSED_FIELD = TraverseStep.ACCESSED_FIELD

    def __init__(self, name_token):
        assert isinstance(
            name_token, Token
        ), f"Expected token, got {type(name_token)}, {name_token}"
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

    def full_name(self):
        result = str(self.name_token)
        for i, step in enumerate(self.traverse_path):
            if step.kind == TraverseStep.DEREFERENCE:
                if i == 0:
                    result = "*" + result
                else:
                    result = f"*({result})"
            else:
                extra = step.kind % str(step.argument)
                result += extra
        return result

    def __str__(self):
        return self.full_name()

    def __repr__(self) -> str:
        return f"Variable({str(self)})"
