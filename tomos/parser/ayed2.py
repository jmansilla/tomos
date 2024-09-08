from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput
from lark.lexer import Token
from lark.tree import Tree

from tomos.expressions.ayed2.types import *
from tomos.expressions.ayed2.expressions import *
from tomos.expressions.ayed2.operators import *

unary_symbols = ' | '.join(map(lambda s:'"%s"'%s, UnaryOpTable.keys()))
binary_symbols = ' | '.join(map(lambda s:'"%s"'%s, BinaryOpTable.keys()))


ayed2_grammar = fr"""
?start: line*

?line: var_declaration
    | assignment
    | function_call

var_declaration: "var" NAME ":" type
assignment: destination ":=" expr

destination: NAME
     | pointed
pointed: "*" NAME

function_call: NAME "(" args ")"
args: expr ("," expr)*

expr: _constant
    | unary_op
    | binary_op
    | function_call
    | NAME

_constant: NUMBER | BOOL
BOOL: "true" | "false"

type: BASIC_TYPE | "pointer of" BASIC_TYPE -> pointer
BASIC_TYPE: "int" | "bool"

unary_op: UNARY_OP expr
binary_op: expr BIN_OP expr
UNARY_OP: {unary_symbols}
BIN_OP: {binary_symbols}

COMMENT: "//" /[^\n]*/

%import common.CNAME            -> NAME
%import common.SIGNED_NUMBER    -> NUMBER

%ignore COMMENT
%import common.WS
%ignore WS
"""


class TreeToAST(Transformer):
    def var_declaration(self, args):
        name, type = args
        return VarDeclaration(name=name, type=type)

    def pointer(self, args):
        assert len(args) == 1
        token = args[0]
        pointed_type = self.type(args)
        return PointerOf(token=token, of=pointed_type)

    def type(self, args):
        assert len(args) == 1
        token = args[0]
        if token.value not in type_map:
            raise UnexpectedInput(f'Unknown type: {token.value}')
        return type_map[token.value](token=token)

    def destination(self, args):
        return args[0]

    def function_call(self, args):
        name, args = args
        return FunctionCall(name=name, args=args)

    def assignment(self, args):
        dest, expr = args
        if isinstance(dest, Variable):
            return Assignment(destination=dest, expr=expr)
        elif isinstance(dest, Tree) and len(dest.children) == 1 and isinstance(dest.children[0], Variable):
            return Assignment(destination=dest.children[0], expr=expr, pointed=True)
        else:
            raise UnexpectedInput(f'Unknown assignment destination: {dest}')

    def NUMBER(self, token):
        if not token.value.isdigit():
            raise UnexpectedInput(f'Invalid number: {token.value}')
        return NaturalConstant(token=token)

    def BOOL(self, token):
        return BooleanConstant(token=token)

    def NAME(self, token):
        return Variable(name=token)

    def unary_op(self, args):
        op, expr = args
        return UnaryOp(op=op, expr=expr)

    def binary_op(self, args):
        left, op, right = args
        return BinaryOp(left=left, op=op, right=right)

    def expr(self, args):
        if len(args) != 1:
            raise UnexpectedInput(f'Invalid expression: {args}')
        return args[0]

    args = list


parser = Lark(ayed2_grammar, start='start', parser='lalr', transformer=TreeToAST())

