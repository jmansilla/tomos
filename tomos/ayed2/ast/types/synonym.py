from .basic import Ayed2Type


class Synonym(Ayed2Type):
    def __init__(self, name, underlying_type):
        self.name = name
        self.underlying_type = underlying_type

    def __call__(self):
        return self

    @property
    def SIZE(self):
        return self.underlying_type.SIZE

    @property
    def is_pointer(self):
        return self.underlying_type.is_pointer

    def is_valid_value(self, value):
        return self.underlying_type.is_valid_value(value)
