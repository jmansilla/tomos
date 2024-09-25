from pathlib import Path

from lark import Lark

from tomos.ayed2.ast.operators import *
from .parsetree_to_ast import TreeToAST


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
