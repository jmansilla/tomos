from tomos.expressions.ayed2.types import *

class Expr:
    pass

class Variable(Expr):
    def __init__(self, name):
        self._token = name

    @property
    def name(self):
        return self._token.value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}({self.name})'


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
        class_name = self.__class__.__name__
        return f'{class_name}({self.op}, {self.expr})'

class BinaryOp(Expr):
    def __init__(self, left, op, right):
        self._left = left
        self._op_token = op
        self._right = right

    @property
    def left(self):
        return self._left

    @property
    def op(self):
        return self._op_token.value

    @property
    def right(self):
        return self._right

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}({self.left}, {self.op}, {self.right})'


class FunctionCall(Expr):
    def __init__(self, name, args):
        self._name = name
        self._args = args

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}({self.name}, {self.args})'


class _Constant(Expr):
    def __init__(self, token):
        self._token = token

    @property
    def value(self):
        return self._token.value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}({self.value})'

class BooleanConstant(_Constant):
    type = BoolType
class NaturalConstant(_Constant):
    type = IntType

class VarDeclaration(Expr):
    def __init__(self, name, type):
        self._variable = name
        self._type = type

    @property
    def name(self):
        return self._variable.name

    @property
    def type(self):
        return self._type

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(name={self.name}, type={self.type})'


class Assignment(Expr):
    def __init__(self, destination, expr, pointed=False):
        self._variable = destination
        self._expr = expr
        self.pointed = pointed

    @property
    def destination(self):
        return self._variable.name

    @property
    def expr(self):
        return self._expr

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        star = '*' if self.pointed else ''
        return f'{class_name}(dest={star}{self.destination}, expr={self.expr})'
