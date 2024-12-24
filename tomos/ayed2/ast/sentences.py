from tomos.ayed2.ast.base import ASTNode
from tomos.ayed2.ast.expressions import Expr, Variable
from tomos.exceptions import TomosSyntaxError


class Sentence(ASTNode):
    next_instruction = None


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
        if not isinstance(then_sentences, list) or not isinstance(else_sentences, list):
            raise TomosSyntaxError("then_sentences and else_sentences must be lists")
        if not isinstance(guard, Expr):
            raise TomosSyntaxError("guard must be an expression")
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
        if not isinstance(sentences, list):
            raise TomosSyntaxError("sentences must be lists")
        elif not sentences:
            raise TomosSyntaxError("sentences must not be empty")
        if not isinstance(guard, Expr):
            raise TomosSyntaxError("guard must be an expression")
        self.guard = guard
        self.sentences = sentences
        last = sentences[-1]
        last.next_instruction = self  # making sure after body is executed we check the guard again

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
    def __init__(self, dest_variable, expr):
        if not isinstance(dest_variable, Variable):
            raise TomosSyntaxError("dest_variable must be a variable")
        if not isinstance(expr, Expr):
            raise TomosSyntaxError("expr must be an expression")
        self.dest_variable = dest_variable
        self.expr = expr

    @property
    def name(self):
        return self.dest_variable.name

    @property
    def line_number(self):
        return self.dest_variable.line_number

    def __repr__(self) -> str:
        full_name = str(self.dest_variable)
        return f"Assignment(dest={full_name}, expr={self.expr})"
