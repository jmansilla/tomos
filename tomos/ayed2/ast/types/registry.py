from tomos.exceptions import TomosTypeError
from .basic import IntType, RealType, BoolType, CharType, Ayed2Type
from .enum import Enum


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
        self._reserved_constant_names = set()

    def register_type(self, name, new_type):
        if not isinstance(new_type, Ayed2Type):
            raise TomosTypeError(f"Cant register type {new_type} because it does not inherit from Ayed2Type.")
        if name in self.type_map:
            raise TomosTypeError(f"Type {name} is already registered.")
        if isinstance(new_type, Enum):
            if self._reserved_constant_names.intersection(new_type.values):
                intersection = self._reserved_constant_names.intersection(new_type.values)
                raise TomosTypeError(f"Type {name} is already registered and has the following constants: {intersection}")
            else:
                self._reserved_constant_names.update(new_type.values)
        self.type_map[name] = new_type

    def get_type(self, name):
        if name not in self.type_map:
            raise TomosTypeError(f"Unknown type: {name}. Available types are: {list(self.type_map.keys())}")
        return self.type_map[name]

    def list_types(self):
        return list(self.type_map.items())


type_registry = TypeRegistry()  # Global type registry