from tomos.exceptions import TomosTypeError
from .basic import IntType, RealType, BoolType, CharType, Ayed2Type
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
            raise TomosTypeError(f"Unknown enum constant: {name}. Available constants are: {list(self.constant_mapping.keys())}")
        return self.constant_mapping[name]



class TypeRegistry:
    def __init__(self):
        # kind of weird coded like this instead of directly in __init__
        # it's useful for testing
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
        if not isinstance(new_type, Ayed2Type):
            raise TomosTypeError(f"Cant register type {new_type} because it does not inherit from Ayed2Type.")
        if name in self.type_map:
            raise TomosTypeError(f"Type {name} is already registered.")
        if isinstance(new_type, Enum):
            overlap = self._enum_constants.get_overlap(new_type.constants)
            if overlap:
                raise TomosTypeError(f"Enum constants overlap: {overlap}")
            else:
                self._enum_constants.update(new_type.constants)
        self.type_map[name] = new_type

    def get_type(self, name):
        if name not in self.type_map:
            raise TomosTypeError(f"Unknown type: {name}. Available types are: {list(self.type_map.keys())}")
        return self.type_map[name]

    def list_types(self):
        return list(self.type_map.items())

    def get_enum_constant(self, name):
        return self._enum_constants.get_constant(name)


type_registry = TypeRegistry()  # Global type registry