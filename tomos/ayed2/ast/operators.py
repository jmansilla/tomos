from tomos.ayed2.ast.expressions import Expr, LazyExpr
from tomos.ayed2.parser.token import Token


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

    @property
    def line_number(self):
        return self.expr.line_number

    def children(self):
        return [self.expr]


class BinaryOp(Expr):

    def __init__(self, left_expr, op_token, right_expr):
        assert (
            isinstance(op_token, Token)
            and isinstance(left_expr, Expr)
            and isinstance(right_expr, Expr)
        )
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

    @property
    def line_number(self):
        return self.left_expr.line_number

    def __repr__(self) -> str:
        return f"BinaryOp({self.left}, {self.op}, {self.right})"

    def is_boolean(self):
        return self.op in ["&&", "||"]

    def children(self):
        if self.is_boolean():
            return [LazyExpr(self.left), LazyExpr(self.right)]
        else:
            return [self.left, self.right]
