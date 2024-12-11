from tomos.exceptions import TomosTypeError
from .basic import IntType, RealType, BoolType, CharType


class TypeRegistry:
    def __init__(self):
        self.load_basic_types()
        # kind of weird coded like this instead of directly in __init__
        # it's useful for testing

    def load_basic_types(self):
        self.type_map = {
            "int": IntType,
            "real": RealType,
            "bool": BoolType,
            "char": CharType,
        }

    def reset(self):
        self.load_basic_types()

    def register_type(self, name, type_factory):
        if name in self.type_map:
            raise TomosTypeError(f"Type {name} is already registered.")
        self.type_map[name] = type_factory

    def get_type(self, name):
        if name not in self.type_map:
            raise TomosTypeError(f"Unknown type: {name}. Available types are: {list(self.type_map.keys())}")
        return self.type_map[name]


type_registry = TypeRegistry()  # Global type registry