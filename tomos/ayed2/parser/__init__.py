from pathlib import Path

from lark import Lark

from .parsetree_to_ast import TreeToAST


def get_grammar_txt():
    grammar_file = Path(__file__).parent.joinpath("grammar.lark")

    grammar_lines = open(grammar_file, "r").readlines()
    grammar_txt = "\n".join(l for l in grammar_lines if not l.startswith("//"))

    return grammar_txt


def build_parser():
    return Lark(get_grammar_txt(), start="program", parser="lalr", transformer=TreeToAST())


parser = build_parser()
