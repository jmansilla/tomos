from tomos.ayed2.expressions.types import *


class Module:
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self) -> str:
        return f"Module({self.children})"

    def pretty(self):
        title = f"module {self.name}\n\t"
        body = '\n\t'.join(map(lambda c: repr(c), self.body))
        return title + body


class Expr:

    def eval(self, state):
        raise NotImplementedError(f"Not implemented for {self.__class__}")


class Variable(Expr):
    def __init__(self, name):
        self._name_token = name

    @property
    def name(self):
        return self._name_token.value

    def __repr__(self) -> str:
        return f"Variable({self.name})"

    def eval(self, state):
        if self.name not in state.stack:
            raise Exception(f"Variable {self.name} is not defined.")
        return state.stack[self.name]


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


class _Constant(Expr):
    def __init__(self, token):
        self._token = token

    @property
    def value(self):
        return self._token.value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.value})"


class BooleanConstant(_Constant):
    type = BoolType


class NaturalConstant(_Constant):
    type = IntType


class VarDeclaration(Expr):
    def __init__(self, name, declared_type):
        self._name_token = name
        self._type = declared_type

    @property
    def name(self):
        return self._name_token.value

    @property
    def type(self):
        return self._type

    def __repr__(self) -> str:
        return f"VarDeclaration(name={self.name}, type={self.type})"


class FunctionDeclaration(Expr):
    def __init__(self, name, args, body):
        self._name_token = name
        self._args = args
        self._body = body

    @property
    def name(self):
        return self._name_token.value

    @property
    def args(self):
        return self._args

    @property
    def body(self):
        return self._body

    def __repr__(self) -> str:
        return f"FunctionDeclaration(name={self.name}, args={self.args}, body={self.body})"


class Assignment(Expr):
    def __init__(self, name, expr, pointed=False):
        self._name_token = name
        self._expr = expr
        self.pointed = pointed

    @property
    def name(self):
        return self._name_token.value

    @property
    def expr(self):
        return self._expr

    def __repr__(self) -> str:
        star = "*" if self.pointed else ""
        return f"FunctionCall(name={star}{self.name}, expr={self.expr})"
