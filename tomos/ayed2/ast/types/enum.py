from .basic import Ayed2Type, IntType
from tomos.exceptions import EnumerationError


class Enum(Ayed2Type):
    def __init__(self, values):
        self.underlying_type = IntType
        for value in values:
            if not isinstance(value, str):
                raise EnumerationError(
                    f"Enum values must be strings, not {type(value)}"
                )
        self.values = values

    def __call__(self):
        return self

    @property
    def SIZE(self):
        return self.underlying_type.SIZE

    @property
    def is_pointer(self):
        return self.underlying_type.is_pointer

    def is_valid_value(self, value):
        return value in self.values
