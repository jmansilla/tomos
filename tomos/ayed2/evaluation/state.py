from tomos.ayed2.ast.types import Ayed2TypeError, PointerOf


class UndeclaredVariableError(Exception):
    pass


class MemoryInfrigementError(Exception):
    pass


class _UnkownSingleton:
    def __repr__(self):
        return "<UnkownValue>"


UnkownValue = _UnkownSingleton()


class State:
    def __init__(self):
        self.allocator = MemoryAllocator()
        self.memory_cells = {}
        self.cell_by_names = {}
        self.heap = {}

    def declare_static_variable(self, name, var_type):
        if name in self.cell_by_names:
            raise Ayed2TypeError(f"Variable {name} already declared.")
        cell = self.allocator.allocate(MemoryAddress.STACK, var_type)
        self.memory_cells[cell.address] = cell
        self.cell_by_names[name] = cell

    def alloc(self, name):
        if name not in self.cell_by_names:
            raise Ayed2TypeError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if not isinstance(cell.var_type, PointerOf):
            raise Ayed2TypeError(f"Cannot allocate. Variable {name} is not a pointer.")
        new_cell = self.allocator.allocate(MemoryAddress.HEAP, cell.var_type._of)
        self.memory_cells[new_cell.address] = new_cell
        self.heap[new_cell.address] = new_cell
        self.cell_by_names[name].value = new_cell.address

    def free(self, name):
        if name not in self.cell_by_names:
            raise Ayed2TypeError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if not isinstance(cell.var_type, PointerOf):
            raise Ayed2TypeError(f"Cannot free. Variable {name} is not a pointer.")
        if cell.value not in self.memory_cells or cell.value not in self.heap:
            raise MemoryInfrigementError()
        del self.memory_cells[cell.value]
        del self.heap[cell.value]
        cell.value = UnkownValue

    def set_static_variable_value(self, name, value, contained_at=False):
        if name not in self.cell_by_names:
            raise Ayed2TypeError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if contained_at:
            assert isinstance(cell.var_type, PointerOf)
            if cell.value not in self.memory_cells:
                raise MemoryInfrigementError()
            cell = self.memory_cells[cell.value]
        if not cell.var_type.is_valid_value(value):
            star = "*" if contained_at else ""
            raise Ayed2TypeError(
                f"Variable {star}{name} was declared of type {cell.var_type}, "
                f"but attempted to set value {value}({type(value)}) that's not valid for this type."
            )
        cell.value = value

    def get_static_variable_value(self, name, address_of=False, contained_at=False):
        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if address_of:
            return cell.address
        else:
            if contained_at:
                assert isinstance(cell.var_type, PointerOf)
                if cell.value not in self.memory_cells:
                    raise MemoryInfrigementError()
                referenced_cell = self.memory_cells[cell.value]
                return referenced_cell.value
            else:
                return cell.value

    def list_declared_variables(self):
        return {name: cell.var_type for name, cell in self.cell_by_names.items()}


class MemoryAllocator:
    def __init__(self):
        self.next_free_address = dict(
            [(partition, 0) for partition in MemoryAddress.PARTITIONS]
        )

    def allocate(self, partition, var_type):
        assert partition in MemoryAddress.PARTITIONS
        address = self.next_free_address[partition]
        self.next_free_address[partition] += var_type.SIZE
        return MemoryCell(MemoryAddress(partition, address), var_type)


class MemoryAddress:
    STACK = 'S'
    HEAP = 'H'
    PARTITIONS = [STACK, HEAP]

    def __init__(self, partition, address):
        assert partition in MemoryAddress.PARTITIONS
        self._partition = partition
        self._address = address

    def __str__(self):
        return f"{self._partition}{self._address:08x}"


class MemoryCell:
    def __init__(self, address, var_type, value=None):
        # Actually, var_type is the number of bits in the cell
        self.address = address
        self.var_type = var_type
        if value is None:
            self.value = UnkownValue
        else:
            self.value = value

