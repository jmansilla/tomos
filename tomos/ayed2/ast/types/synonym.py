from tomos.exceptions import SynonymError
from .basic import Ayed2Type


class Synonym(Ayed2Type):
    def __init__(self, underlying_type):
        if not isinstance(underlying_type, Ayed2Type):
            raise SynonymError(f"Cant create a synonym of {underlying_type},"
                               f" expected Ayed2Type instance, got {type(underlying_type)} instead.")
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
