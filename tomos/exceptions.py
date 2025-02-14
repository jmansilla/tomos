
class TomosException(Exception):
    """Base class for custom exceptions in this project."""
    pass


class TomosTypeError(TomosException):
    pass


class TomosSyntaxError(TomosException):
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
