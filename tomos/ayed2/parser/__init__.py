from pathlib import Path

from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput
from lark.lexer import Token
from lark.tree import Tree

from tomos.ayed2.ast.types import *
from tomos.ayed2.ast.expressions import *
from tomos.ayed2.ast.sentences import *
from tomos.ayed2.ast.operators import *
from tomos.ayed2.ast.program import *


class TreeToAST(Transformer):

    def program(self, args):
        tdef, fdef, body = args
        return Program(typedef_section=tdef.children, funprocdef_section=fdef.children, body=body)

    def body(self, args):
        vardef, sentences = args
        return Body(var_declarations=vardef.children, sentences=sentences.children)

    def vname(self, args):
        assert len(args) == 1
        return args[0]

    def SKIP(self, token):
        return Skip(token)

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

    def builtin_call(self, args):
        name, *call_args = args
        return BuiltinCall(name=name, args=call_args)

    # def function_call(self, args):
    #     name, args = args
    #     return FunctionCall(name=name, args=args)

    def assignment(self, args):
        dest, expr = args
        return Assignment(dest=dest, expr=expr)

    def NUMBER(self, token):
        if not token.value.isdigit():
            raise UnexpectedInput(f"Invalid number: {token.value}")
        return IntegerConstant(token=token)

    def BOOL(self, token):
        return BooleanConstant(token=token)

    def unary_op(self, args):
        op, expr = args
        return UnaryOp(op=op, expr=expr)

    def binary_op(self, args):
        left, op, right = args
        return BinaryOp(left=left, op=op, right=right)

    def variable(self, args):
        return Variable(name=args[0])

    def address_of(self, args):
        var = args[0]
        var._address_of = True
        return var

    def contained_at(self, args):
        var = args[0]
        var._contained_at = True
        return var

    def expr(self, args):
        if len(args) != 1:
            raise UnexpectedInput(f"Invalid expression: {args}")
        return args[0]

    args = list


def build_parser():
    unary_symbols = " | ".join(map(lambda s: '"%s"' % s, UnaryOpTable.keys()))
    binary_symbols = " | ".join(map(lambda s: '"%s"' % s, BinaryOpTable.keys()))

    grammar_file = Path(__file__).parent.joinpath("grammar.lark")

    grammar_lines = open(grammar_file, "r").readlines()
    grammar_txt = "\n".join(l for l in grammar_lines if not l.startswith("//"))
    ayed2_grammar = grammar_txt.format(
        unary_symbols=unary_symbols,
        binary_symbols=binary_symbols
    )

    return Lark(ayed2_grammar, start="program", parser="lalr", transformer=TreeToAST())


parser = build_parser()
