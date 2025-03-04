from tomos.exceptions import SynonymError
from .basic import Ayed2Type, UserDefinedType


class Synonym(UserDefinedType):
    CLOSURE_LIMIT = 10

    def __init__(self, underlying_type):
        if not isinstance(underlying_type, Ayed2Type):
            raise SynonymError(
                f"Cant create a synonym of {underlying_type},"
                f" expected Ayed2Type instance, got {type(underlying_type)} instead."
            )
        self.underlying_type = underlying_type

    def __call__(self):
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.underlying_type}"

    def underlying_type_closure(self):
        u_type = self.underlying_type
        i = 0
        while isinstance(u_type, Synonym):
            u_type = u_type.underlying_type
            i += 1
            if i >= self.CLOSURE_LIMIT:
                raise SynonymError(f"Synonym closure limit ({self.CLOSURE_LIMIT}) exceeded")
        return u_type

    @property
    def SIZE(self):
        return self.underlying_type.SIZE

    @property
    def is_pointer(self):
        return self.underlying_type.is_pointer

    def is_valid_value(self, value):
        return self.underlying_type.is_valid_value(value)

    def has_deferrals(self, crumbs=[]):
        if self in crumbs:
            return False  # avoid infinite loop
        return self.underlying_type.has_deferrals(crumbs + [self])

    def resolve_deferrals(self, crumbs=[]):
        if self.underlying_type.has_deferrals(crumbs + [self]):
            self.underlying_type.resolve_deferrals(crumbs + [self])
        return self
