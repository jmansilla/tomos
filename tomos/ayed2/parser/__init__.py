from pathlib import Path

from lark import Lark

from .parsetree_to_ast import TreeToAST


def get_grammar_txt():
    grammar_file = Path(__file__).parent.joinpath("grammar.lark")
    grammar_lines = open(grammar_file, "r").readlines()
    grammar_txt = "\n".join(l for l in grammar_lines if not l.startswith("//"))
    return grammar_txt


class TomosParser(Lark):

    def parse(self, *args, **kwargs):
        from tomos.ayed2.ast.types.registry import type_registry  # avoid circular import
        parse_results = super().parse(*args, **kwargs)
        type_registry.resolve_deferred_types()
        return parse_results


def build_parser():
    return TomosParser(get_grammar_txt(), start="program", parser="lalr", transformer=TreeToAST())


parser = build_parser()
