from tomos.ayed2.ast.base import ASTNode
from tomos.ayed2.ast.sentences import Variable
from tomos.ayed2.ast.types import Ayed2Type
from tomos.ayed2.parser.token import Token
from tomos.base_classes.dataclasses import dataclass


class ProgramExpression(ASTNode):
    next_instruction = None


class Program(ProgramExpression):
    def __init__(self, typedef_section, funprocdef_section, body):
        self.typedef_section = typedef_section
        self.funprocdef_section = funprocdef_section
        self.body = body

    def __repr__(self) -> str:
        return f"Program({self.body})"


class Body(ProgramExpression):
    def __init__(self, var_declarations, sentences):
        assert all(isinstance(v, VarDeclaration) for v in var_declarations)
        self.var_declarations = var_declarations
        from tomos.ayed2.ast.sentences import Sentence  # avoid circular import

        assert all(isinstance(s, Sentence) for s in sentences)
        self.sentences = sentences

    def __iter__(self):
        yield from self.var_declarations
        yield from self.sentences


@dataclass
class VarDeclaration(ProgramExpression):
    variable: Variable
    var_type: Ayed2Type

    @property
    def name(self):
        return self.variable.name

    @property
    def line_number(self):
        return self.variable.line_number

    def __repr__(self) -> str:
        return f"VarDeclaration(name={self.name}, type={self.var_type})"


@dataclass
class TypeDeclaration(ProgramExpression):
    name: Token
    new_type: Ayed2Type

    @property
    def line_number(self):
        return self.name.line

    def __repr__(self) -> str:
        return f"TypeDeclaration(name={self.name}, type={self.new_type})"


class FunctionDeclaration(ProgramExpression):
    # TODO
    pass


class ProcedureDeclaration(ProgramExpression):
    # TODO
    pass
