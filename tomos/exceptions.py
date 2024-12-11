
class TomosException(Exception):
    """Base class for custom exceptions in this project."""
    pass


class TomosTypeError(TomosException):
    pass


class ExpressionEvaluationError(TomosException):
    pass


class AlreadyDeclaredVariableError(TomosException):
    pass


class MemoryInfrigementError(TomosException):
    pass


class UndeclaredVariableError(TomosException):
    pass
