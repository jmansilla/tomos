from dataclasses import dataclass
from copy import copy


class Sentence:
    pass


class Skip(Sentence):
    def __init__(self, token):
        self.token = token

    @property
    def line_number(self):
        return self.token.line

    def __repr__(self) -> str:
        return "Skip()"


class ProcedureCall(Sentence):
    # TODO
    pass


class BuiltinCall(Sentence):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @property
    def line_number(self):
        return self.name.line

    def __repr__(self) -> str:
        return f"BuiltinCall(name={self.name}, args={self.args})"


class If(Sentence):
    def __init__(self, guard, then_sentences, else_sentences):
        self.guard = guard
        self.then_sentences = then_sentences
        self.else_sentences = else_sentences

    @property
    def line_number(self):
        return self.guard.line_number

    def __repr__(self) -> str:
        return f"If(guard={self.guard})"


class While(Sentence):
    def __init__(self, guard, sentences):
        self.guard = guard
        self.sentences = sentences

    @property
    def line_number(self):
        return self.guard.line_number

    def __repr__(self) -> str:
        return f"While(guard={self.guard})"


class For(Sentence):
    def __init__(self, name, start, end, sentences):
        self.name_token = name
        self.start = start
        self.end = end
        self.sentences = sentences


class Assignment(Sentence):
    @dataclass
    class Modifiers:
        dereferenced: bool
        array_indexing: list

    def __init__(self, dest_variable, expr):
        self.dest_variable = dest_variable
        self.expr = expr

    @property
    def name(self):
        return self.dest_variable.name

    @property
    def line_number(self):
        return self.dest_variable.line_number

    @property
    def modifiers(self):
        return self.Modifiers(
            dereferenced=self.dest_variable.dereferenced,
            array_indexing=copy(self.dest_variable.array_indexing),
        )

    def __repr__(self) -> str:
        full_name = self.dest_variable.symbols_name
        full_name = str(self.dest_variable)
        return f"Assignment(dest={full_name}, expr={self.expr})"
