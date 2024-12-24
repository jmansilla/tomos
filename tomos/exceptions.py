
class TomosException(Exception):
    """Base class for custom exceptions in this project."""
    pass


class TomosTypeError(TomosException):
    pass


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