
class TomosException(Exception):
    """Base class for custom exceptions in this project."""
    pass


class TomosTypeError(TomosException):
    pass


class ExpressionEvaluationError(TomosException):
    pass