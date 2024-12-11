from .basic import Ayed2Type


class Synonym(Ayed2Type):
    def __init__(self, name, underlying_type):
        self.name = name
        self.underlying_type = underlying_type

    def __call__(self):
        return self
