from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput
from lark.lexer import Token
from lark.tree import Tree

from tomos.ayed2.expressions.types import *
from tomos.ayed2.expressions.expressions import *
from tomos.ayed2.expressions.operators import *

unary_symbols = " | ".join(map(lambda s: '"%s"' % s, UnaryOpTable.keys()))
binary_symbols = " | ".join(map(lambda s: '"%s"' % s, BinaryOpTable.keys()))


ayed2_grammar = rf"""
?module: line*

?line: var_declaration
    | assignment
    | function_call

var_declaration: "var" vname ":" type
assignment: destination ":=" expr

vname : NAME
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

    # def __default__(self, data, children, meta):
    #     r = super(TreeToAST, self).__default__(data, children, meta)
    #     if data in ['__start_star_0', '_constant']:
    #         return r
    #     print('default', '1-', type(data), '2-', data, '3-', children, '4-', meta)
    #     return r

    def module(self, args):
        return Module(name='', body=args)

    def vname(self, args):
        assert len(args) == 1
        return args[0]

    def var_declaration(self, args):
        name, declared_type = args
        return VarDeclaration(name=name, declared_type=declared_type)

    def pointer(self, args):
        assert len(args) == 1
        token = args[0]
        pointed_type = self.type(args)
        return PointerOf(token=token, of=pointed_type)

    def type(self, args):
        assert len(args) == 1
        token = args[0]
        if token.value not in type_map:
            raise UnexpectedInput(f"Unknown type: {token.value}")
        return type_map[token.value](token=token)

    def destination(self, args):
        return args[0]

    def function_call(self, args):
        name, args = args
        return FunctionCall(name=name, args=args)

    def assignment(self, args):
        dest, expr = args
        if isinstance(dest, Token):
            return Assignment(name=dest, expr=expr)
        else:
            if isinstance(dest.data, Token) and dest.data.value == "pointed":
                return Assignment(name=dest.children[0], expr=expr, pointed=True)
            else:
                raise UnexpectedInput(f"Unknown assignment destination: {dest}")

    def NUMBER(self, token):
        if not token.value.isdigit():
            raise UnexpectedInput(f"Invalid number: {token.value}")
        return NaturalConstant(token=token)

    def BOOL(self, token):
        return BooleanConstant(token=token)

    def unary_op(self, args):
        op, expr = args
        return UnaryOp(op=op, expr=expr)

    def binary_op(self, args):
        left, op, right = args
        return BinaryOp(left=left, op=op, right=right)

    def expr(self, args):
        if len(args) != 1:
            raise UnexpectedInput(f"Invalid expression: {args}")
        return args[0]

    args = list


parser = Lark(ayed2_grammar, start="module", parser="lalr", transformer=TreeToAST())
