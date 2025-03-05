# This module is named t_tuple to avoid clashes with the python tuple class

from tomos.exceptions import TomosTypeError
from .basic import Ayed2Type, UserDefinedType


class Tuple(UserDefinedType):
    def __init__(self, fields_mapping):
        if not isinstance(fields_mapping, dict):
            raise TomosTypeError(f"Expected dict, got {type(fields_mapping)} instead.")
        if len(fields_mapping) == 0:
            raise TomosTypeError("Tuple must have at least one field.")
        self.tuple_size = 0
        for k, t in fields_mapping.items():
            if not isinstance(k, str):
                raise TomosTypeError(
                    f"Declaring Tuple, field name must be a string. Got {type(k)} instead."
                )
            if not isinstance(t, Ayed2Type):
                raise TomosTypeError(
                    f"Declaring Tuple, field type. Expected Ayed2Type, got {type(t)} instead."
                )
            self.tuple_size += t.SIZE  # type: ignore
        self.fields_mapping = fields_mapping

    def __call__(self):
        return self

    @property
    def SIZE(self):
        return self.tuple_size

    def has_deferrals(self, crumbs=[]):
        for key, subtype in self.fields_mapping.items():
            if subtype.has_deferrals(crumbs + [self]):
                return True
        return False

    def resolve_deferrals(self, crumbs=[]):
        for key, subtype in list(self.fields_mapping.items()):
            if subtype.has_deferrals(crumbs + [self]):
                self.fields_mapping[key] = subtype.resolve_deferrals(crumbs + [self])
        return self
