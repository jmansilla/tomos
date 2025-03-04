from tomos.ayed2.evaluation.limits import LIMITER
from tomos.exceptions import TomosTypeError
from .basic import IntType, RealType, BoolType, CharType, UserDefinedType
from .enum import Enum


class EnumConstantsRegistry:
    def __init__(self):
        self.constant_mapping = {}

    def get_overlap(self, new_constants_map):
        current_names = set(self.constant_mapping.keys())
        new_names = set(new_constants_map.keys())
        return current_names.intersection(new_names)

    def update(self, new_constants_map):
        self.constant_mapping.update(new_constants_map)

    def get_constant(self, name):
        if not name in self.constant_mapping:
            raise TomosTypeError(
                f"Unknown enum constant: {name}. Available constants are: {list(self.constant_mapping.keys())}"
            )
        return self.constant_mapping[name]


class TypeRegistry:
    class Deferred:
        is_deferred = True

        def __init__(self, name, reg):
            self.name = name
            self.registry = reg

        def resolve(self):
            factory = self.registry.get_type_factory(self.name)
            return factory()

        def __repr__(self):
            return f"Deferred({self.name})"

    def __init__(self):
        self.reset()

    def load_basic_types(self):
        self.type_map = {
            "int": IntType,
            "real": RealType,
            "bool": BoolType,
            "char": CharType,
        }

    def reset(self):
        self.load_basic_types()
        self._enum_constants = EnumConstantsRegistry()

    def register_type(self, name, new_type):
        name = str(name)  # get rid of Token objects
        if not isinstance(new_type, UserDefinedType):
            raise TomosTypeError(
                f"Cant register type {new_type} because it does not inherit from UserDefinedType."
            )
        if name in self.type_map:
            raise TomosTypeError(f"Type {name} is already registered.")
        if isinstance(new_type, Enum):
            overlap = self._enum_constants.get_overlap(new_type.constants)
            if overlap:
                raise TomosTypeError(f"Enum constants overlap: {overlap}")
            else:
                self._enum_constants.update(new_type.constants)
        LIMITER.check_type_sizing_limits(new_type)
        new_type.name = name  # type: ignore
        self.type_map[name] = new_type

    def get_type_factory(self, name, deferred_if_not_found=False):
        if name not in self.type_map:
            if deferred_if_not_found:
                return self.Deferred(name, self)
            raise TomosTypeError(
                f"Unknown type: {name}. Available types are: {list(self.type_map.keys())}"
            )
        return self.type_map[name]

    def list_types(self):
        return list(self.type_map.items())

    def get_enum_constant(self, name):
        return self._enum_constants.get_constant(name)

    def resolve_deferred_types(self):
        for name, factory in list(self.type_map.items()):
            if isinstance(factory, self.Deferred):
                raise TomosTypeError(f"Deferred type {name} has not been resolved yet.")
            if factory.has_deferrals():
                self.type_map[name] = factory.resolve_deferrals()

    def merge(self, other):
        self.type_map.update(other.type_map)
        new_enum_constants = other._enum_constants.constant_mapping
        if self._enum_constants.get_overlap(new_enum_constants):
            raise TomosTypeError(
                f"Enum constants overlap: {self._enum_constants.get_overlap(new_enum_constants)}"
            )
        self._enum_constants.update(new_enum_constants)


type_registry = TypeRegistry()  # Global type registry
