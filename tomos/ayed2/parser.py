from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput
from lark.lexer import Token
from lark.tree import Tree

from tomos.ayed2.ast.types import *
from tomos.ayed2.ast.expressions import *
from tomos.ayed2.ast.sentences import *
from tomos.ayed2.ast.operators import *

unary_symbols = " | ".join(map(lambda s: '"%s"' % s, UnaryOpTable.keys()))
binary_symbols = " | ".join(map(lambda s: '"%s"' % s, BinaryOpTable.keys()))


#  The Abstract Syntax Tree of the AYED2 language
#  ==============================================
#
#  Expressions
#  ===========
#      ⟨expression⟩ ::= ⟨constant⟩ | ⟨functioncall⟩ | ⟨operation⟩ | ⟨variable〉
#      ⟨constant⟩ ::= ⟨integer⟩ | ⟨real⟩ | ⟨bool⟩ | ⟨character⟩ | ⟨enum_name⟩ | inf | null
#      ⟨functioncall⟩ ::= ⟨id⟩ ( ⟨expression⟩ ... ⟨expression⟩ )
#      ⟨operation⟩ ::= ⟨expression⟩ ⟨binary⟩ ⟨expression⟩ | ⟨unary⟩ ⟨expression⟩
#      ⟨binary⟩ ::= + | − | * | / | % | || | && | <= | >= | < | > | == | !=
#      ⟨unary⟩ ::= - | !
#      ⟨variable⟩ ::= ⟨id⟩
#                   | ⟨variable⟩[⟨expression⟩ ... ⟨expression⟩ ]
#                   | ⟨variable⟩.⟨fname⟩
#                   | *⟨variable⟩
#
#  Sentences
#  =========
#      ⟨sentence⟩ ::= skip | ⟨assignment⟩ | ⟨procedurecall⟩ | ⟨if⟩ | ⟨while⟩ | ⟨for⟩
#      ⟨assignment⟩ ::= ⟨variable⟩ := ⟨expression⟩
#      ⟨while⟩ ::= while ⟨expression⟩ do ⟨sentences⟩
#      ⟨sentences⟩ ::= ⟨sentence⟩ ... ⟨sentence⟩
#
#      ⟨procedurecall⟩ ::= ⟨id⟩ ( ⟨expression⟩ ... ⟨expression⟩ )
#                        | alloc ( ⟨variable⟩ )
#                        | free  ( ⟨variable⟩ )
#
#      ⟨if⟩ ::= if ⟨expression⟩ then ⟨sentences⟩ else ⟨sentences⟩
#      ⟨for⟩ ::= for ⟨id⟩ := ⟨expression⟩ to ⟨expression⟩ do ⟨sentences⟩
#              | for ⟨id⟩ := ⟨expression⟩ downto ⟨expression⟩ do ⟨sentences⟩
#
#  Types
#  =====
#      ⟨type⟩ ::= int | real | bool | char
#               | ⟨array⟩
#               | ⟨pointer⟩
#               | ⟨defined_type⟩
#               | ⟨typevariable⟩
#
#      ⟨array⟩ ::= array ⟨arraysize⟩ ... ⟨arraysize⟩ of ⟨type⟩
#      ⟨arraysize⟩ ::= ⟨natural⟩ | ⟨sname⟩
#      ⟨pointer⟩ ::= pointer ⟨type⟩
#
#      ⟨typevariable⟩ ::= ⟨typeid⟩
#      ⟨defined_type⟩ ::= ⟨tname⟩ of ⟨type⟩ ... ⟨type⟩
#
#      ⟨io⟩ ::= in | out | in/out
#
#      ⟨class⟩ ::= Eq | Ord
#
#      ⟨typedecl⟩ ::= enum ⟨tname⟩ = ⟨cname⟩ ... ⟨cname⟩
#                   | syn ⟨tname⟩ of ⟨typearguments⟩ = ⟨type⟩
#                   | tuple ⟨tname⟩ of ⟨typearguments⟩ = ⟨field⟩ ... ⟨field⟩
#      ⟨typearguments⟩ ::= ⟨typevariable⟩ ... ⟨typevariable⟩
#      ⟨field⟩ ::= ⟨fname⟩ : ⟨type⟩
#
#  Program
#  =======
#      ⟨program⟩ ::= ⟨typedecl⟩ ... ⟨typedecl⟩ ⟨funprocdecl⟩ ... ⟨funprocdecl⟩
#      ⟨funprocdecl⟩ ::= ⟨function⟩ | ⟨procedure⟩

#      ⟨body⟩ ::= ⟨variabledecl⟩ ... ⟨variabledecl⟩ ⟨sentences⟩
#      ⟨variabledecl⟩ ::= var ⟨id⟩ ... ⟨id⟩ : ⟨type⟩

#      ⟨function⟩ ::= fun ⟨id⟩ ( ⟨funargument⟩ ... ⟨funargument⟩ ) ret ⟨funreturn⟩
#                     where ⟨constraints⟩
#                     in ⟨body⟩
#      ⟨funargument⟩ ::= ⟨id⟩ : ⟨type⟩
#      ⟨funreturn⟩ ::= ⟨id⟩ : ⟨type⟩

#      ⟨procedure⟩ ::= proc ⟨id⟩ ( ⟨procargument⟩ ... ⟨procargument⟩ )
#                      where ⟨constraints⟩
#                      in ⟨body⟩
#      ⟨procargument⟩ ::= ⟨io⟩ ⟨id⟩ : ⟨type⟩

#      ⟨constraints⟩ ::= ⟨constraint⟩ ... ⟨constraint⟩
#      ⟨constraint⟩ ::= ⟨typevariable⟩ : ⟨class⟩ ... ⟨class⟩


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
