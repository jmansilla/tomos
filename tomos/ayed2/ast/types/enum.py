from .basic import IntType, UserDefinedType
from tomos.exceptions import EnumerationError


class Enum(UserDefinedType):
    name = None

    def __init__(self, constant_names):
        self.underlying_type = IntType
        for value in constant_names:
            if not isinstance(value, str):
                raise EnumerationError(f"Enum constant_names must be strings, not {type(value)}")
        self.constants = {
            name: EnumConstant(self, name, value)
            for value, name in enumerate(constant_names, start=1)
        }

    def __call__(self):
        return self

    @property
    def SIZE(self):
        return self.underlying_type.SIZE

    @property
    def is_pointer(self):
        return self.underlying_type.is_pointer

    def is_valid_value(self, value):
        if isinstance(value, str):
            return value in self.constants
        if isinstance(value, EnumConstant):
            return value in self.constants.values()


class EnumConstant:
    def __init__(self, enum, name, value):
        self.enum = enum
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}({self.enum})"
