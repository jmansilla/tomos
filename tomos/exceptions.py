class TomosException(Exception):
    """Base class for custom exceptions in this project."""

    pass


class TomosTypeError(TomosException):
    pass


class TomosSyntaxError(TomosException):
    def __init__(self, msg, guess_line_nr_from=None, **kwargs):
        self.guess_from = guess_line_nr_from
        self.base_msg = msg
        msg = self.build_msg()
        super().__init__(msg, **kwargs)

    def build_msg(self):
        line_nr = self.guess_line_number(self.guess_from)
        if line_nr is None:
            return self.base_msg
        else:
            return f"On line {line_nr}: {self.base_msg}."

    def guess_line_number(self, data):
        from tomos.ayed2.parser.token import Token
        from tomos.ayed2.ast.expressions import Expr
        from tomos.ayed2.ast.program import ProgramExpression
        from tomos.ayed2.ast.sentences import Sentence

        if isinstance(data, Token):
            return data.line
        elif isinstance(data, (tuple, list)):
            for item in data:
                recursive = self.guess_line_number(item)
                if recursive is not None:
                    return recursive
        elif isinstance(data, (Sentence, ProgramExpression, Expr)):
            return data.line_number
        else:
            return None


class TomosRuntimeError(TomosException):
    pass


class ExpressionEvaluationError(TomosException):
    pass


class AlreadyDeclaredVariableError(TomosException):
    pass


class MemoryInfrigementError(TomosException):
    pass


class UndeclaredVariableError(TomosException):
    pass


class EnumerationError(TomosException):
    pass


class SynonymError(TomosException):
    pass


class CantDrawError(TomosException):
    pass


# LIMIT ERRORS
class LimitError(TomosException):
    # base class, not to be raised directly
    pass


class ArraySizeLimitExceededError(LimitError):
    pass


class ArrayDimensionsLimitExceededError(LimitError):
    pass


class TupleSizeLimitExceededError(LimitError):
    pass


class ExecutionStepsLimitExceededError(LimitError):
    pass


class MemoryLimitExceededError(LimitError):
    pass


class TypeCompositionLimitExceededError(LimitError):
    pass
