from tomos.ayed2.ast.types import PointerOf, ArrayOf
from tomos.exceptions import AlreadyDeclaredVariableError, MemoryInfrigementError, TomosTypeError, UndeclaredVariableError
from tomos.ayed2.evaluation.memory import MemoryAllocator, MemoryAddress
from tomos.ayed2.evaluation.unknown_value import UnknownValue


class State:
    def __init__(self):
        self.allocator = MemoryAllocator()
        self.memory_cells = dict()
        self.cell_by_names = dict()
        self.heap = dict()

    def declare_static_variable(self, name, var_type):
        if name in self.cell_by_names:
            raise AlreadyDeclaredVariableError(f"Variable {name} already declared.")
        cell = self.allocator.allocate(MemoryAddress.STACK, var_type)
        self.memory_cells[cell.address] = cell
        self.cell_by_names[name] = cell

    def alloc(self, name):
        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if not cell.var_type.is_pointer:
            raise TomosTypeError(f"Cannot allocate. Variable {name} is not a pointer.")
        new_cell = self.allocator.allocate(MemoryAddress.HEAP, cell.var_type.of)
        self.memory_cells[new_cell.address] = new_cell
        self.heap[new_cell.address] = new_cell
        self.cell_by_names[name].value = new_cell.address

    def free(self, name):
        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if not cell.var_type.is_pointer:
            raise TomosTypeError(f"Cannot free. Variable {name} is not a pointer.")
        if cell.value not in self.memory_cells or cell.value not in self.heap:
            raise MemoryInfrigementError()
        del self.memory_cells[cell.value]
        del self.heap[cell.value]
        cell.value = UnknownValue

    def set_variable_value(self, name, value, modifiers=None):
        dereferenced = getattr(modifiers, "dereferenced", False)
        array_indexing = getattr(modifiers, "array_indexing", None)

        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if dereferenced:
            assert cell.var_type.is_pointer
            if cell.value not in self.memory_cells:
                raise MemoryInfrigementError()
            cell = self.memory_cells[cell.value]
        if not cell.var_type.is_valid_value(value):
            star = "*" if dereferenced else ""
            raise TomosTypeError(
                f"Variable {star}{name} was declared of type {cell.var_type}, "
                f"but attempted to set value {value}({type(value)}) that's not valid for this type."
            )
        if array_indexing:
            assert isinstance(cell.var_type, ArrayOf)
            cell[array_indexing] = value
        else:
            assert not isinstance(cell.var_type, ArrayOf)
            cell.value = value

    def get_variable_value(self, name, dereferenced=False, array_indexing=None):
        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        root_cell = self.cell_by_names[name]
        if dereferenced:
            assert root_cell.var_type.is_pointer
            if root_cell.value not in self.memory_cells:
                raise MemoryInfrigementError()
            cell = self.memory_cells[root_cell.value]
        else:
            cell = root_cell
        if array_indexing:
            assert isinstance(cell.var_type, ArrayOf)
            return cell[array_indexing]
        else:
            assert not isinstance(cell.var_type, ArrayOf)
            return cell.value

    def list_declared_variables(self):
        return {name: cell.var_type for name, cell in self.cell_by_names.items()}

