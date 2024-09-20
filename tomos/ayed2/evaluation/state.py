from tomos.ayed2.ast.types import Ayed2TypeError


class UndeclaredVariableError(Exception):
    pass


UnkownValue = object()


class State:
    def __init__(self):
        self.stack = {}
        self.stack_types = {}

    def declare_static_variable(self, name, var_type):
        if name in self.stack_types:
            raise Ayed2TypeError(f"Variable {name} already declared.")
        self.stack_types[name] = var_type

    def set_static_variable_value(self, name, value, var_type):
        if name not in self.stack_types:
            raise Ayed2TypeError(f"Variable {name} is not declared.")
        if self.stack_types[name] != var_type:
            raise Ayed2TypeError(
                f"Variable {name} was declared of type {self.stack_types[name]}, "
                 "but attempted to set value of type {var_type}.")
        self.stack[name] = value

    def get_static_variable_value(self, name):
        if name not in self.stack_types:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        if name not in self.stack:
            return UnkownValue
        return self.stack[name]

    def list_declared_variables(self):
        return dict(self.stack_types)
