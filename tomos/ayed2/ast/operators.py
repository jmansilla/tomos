from tomos.ayed2.ast.expressions import Expr


UnaryOpTable = {
    "-": "Negative",
    "+": "Positive",
    "!": "Not",
}

BinaryOpTable = {
    "+": "Sum",
    "-": "Minus",
    "*": "Times",
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
    def __init__(self, op, expr):
        self._op_token = op
        self._expr = expr

    @property
    def op(self):
        return self._op_token.value

    @property
    def expr(self):
        return self._expr

    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, {self.expr})"

    def children(self):
        yield self.expr


class BinaryOp(Expr):
    def __init__(self, left, op, right):
        self._left_expr = left
        self._op_token = op
        self._right_expr = right

    @property
    def left(self):
        return self._left_expr

    @property
    def op(self):
        return self._op_token.value

    @property
    def right(self):
        return self._right_expr

    def __repr__(self) -> str:
        return f"BinaryOp({self.left}, {self.op}, {self.right})"

    def children(self):
        yield self.left
        yield self.right