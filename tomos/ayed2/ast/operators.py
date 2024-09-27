from lark.lexer import Token
from tomos.ayed2.ast.expressions import Expr


UnaryOpTable = {
    "-": "Negative",
    "+": "Positive",
    "!": "Not",
}

BinaryOpTable = {
    "*": "Times",
    "+": "Sum",
    "-": "Minus",
    "/": "Div",
    "%": "Reminder",
    "||": "Or",
    "&&": "And",
    "==": "Equal",
    "!=": "NotEqual",
    "<": "LessThan",
    "<=": "LessThanEqual",
    ">": "MoreThan",
    ">=": "MoreThanEqual",
}


class UnaryOp(Expr):
    def __init__(self, op_token, expr):
        assert isinstance(op_token, Token) and isinstance(expr, Expr)
        self.op_token = op_token
        self.expr = expr

    @property
    def op(self):
        return self.op_token.value

    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, {self.expr})"

    def children(self):
        return [self.expr]


class BinaryOp(Expr):
    def __init__(self, left_expr, op_token, right_expr):
        assert isinstance(op_token, Token) and isinstance(left_expr, Expr) and isinstance(right_expr, Expr)
        self.left_expr = left_expr
        self.op_token = op_token
        self.right_expr = right_expr

    @property
    def left(self):
        return self.left_expr

    @property
    def op(self):
        return self.op_token.value

    @property
    def right(self):
        return self.right_expr

    def __repr__(self) -> str:
        return f"BinaryOp({self.left}, {self.op}, {self.right})"

    def children(self):
        return [self.left, self.right]
