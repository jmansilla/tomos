from tomos.ayed2.ast.types import Ayed2TypeError, PointerOf, ArrayOf


class UndeclaredVariableError(Exception):
    pass


class AlreadyDeclaredVariableError(Exception):
    pass


class MemoryInfrigementError(Exception):
    pass


class _UnkownSingleton:
    def __repr__(self):
        return "<?>"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, _UnkownSingleton):
            return True
        return False

    def __hash__(self) -> int:
        return str(self).__hash__()


UnkownValue = _UnkownSingleton()


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
        if not isinstance(cell.var_type, PointerOf):
            raise Ayed2TypeError(f"Cannot allocate. Variable {name} is not a pointer.")
        new_cell = self.allocator.allocate(MemoryAddress.HEAP, cell.var_type.of)
        self.memory_cells[new_cell.address] = new_cell
        self.heap[new_cell.address] = new_cell
        self.cell_by_names[name].value = new_cell.address

    def free(self, name):
        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if not isinstance(cell.var_type, PointerOf):
            raise Ayed2TypeError(f"Cannot free. Variable {name} is not a pointer.")
        if cell.value not in self.memory_cells or cell.value not in self.heap:
            raise MemoryInfrigementError()
        del self.memory_cells[cell.value]
        del self.heap[cell.value]
        cell.value = UnkownValue

    def set_variable_value(self, name, value, modifiers=None):
        dereferenced = getattr(modifiers, "dereferenced", False)
        array_indexing = getattr(modifiers, "array_indexing", None)

        if name not in self.cell_by_names:
            raise UndeclaredVariableError(f"Variable {name} is not declared.")
        cell = self.cell_by_names[name]
        if dereferenced:
            assert isinstance(cell.var_type, PointerOf)
            if cell.value not in self.memory_cells:
                raise MemoryInfrigementError()
            cell = self.memory_cells[cell.value]
        if not cell.var_type.is_valid_value(value):
            star = "*" if dereferenced else ""
            raise Ayed2TypeError(
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
            assert isinstance(root_cell.var_type, PointerOf)
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


class MemoryAllocator:
    def __init__(self):
        self.next_free_address = dict(
            [(partition, 0) for partition in MemoryAddress.PARTITIONS]
        )

    def allocate(self, partition, var_type):
        assert partition in MemoryAddress.PARTITIONS
        if isinstance(var_type, ArrayOf):
            elements = []

            for i in range(var_type.number_of_elements()):
                elements.append(self.allocate(partition, var_type.of))

            return ArrayCellCluster(var_type, elements)
        else:
            address = self.next_free_address[partition]
            cell = MemoryCell(MemoryAddress(partition, address), var_type)
            self.next_free_address[partition] += var_type.SIZE  # type: ignore
            return cell


class MemoryAddress:
    STACK = 'S'
    HEAP = 'H'
    PARTITIONS = [STACK, HEAP]

    def __init__(self, partition, address):
        assert partition in MemoryAddress.PARTITIONS
        self.partition = partition
        self.address = address

    def __str__(self):
        return f"{self.partition}{self.address:05x}"

    def __repr__(self) -> str:
        return f"MemoryAddress({self.partition}, {self.address})"

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.partition, self.address))


class MemoryCell:
    def __init__(self, address, var_type, value=None):
        assert isinstance(address, MemoryAddress)
        self.address = address
        self.var_type = var_type
        if value is None:
            self.value = UnkownValue
        else:
            self.value = value


class ArrayCellCluster:
    def __init__(self, array_type, elements):
        assert isinstance(array_type, ArrayOf)
        self.array_type = array_type
        self.elements = elements

    @property
    def var_type(self):
        return self.array_type

    @property
    def address(self):
        return self.elements[0].address

    @property
    def value(self):
        # used by the UIs
        return [cell.value for cell in self.elements]

    def __setitem__(self, key, value):
        idx = self.array_type.flatten_index(key)
        self.elements[idx].value = value

    def __getitem__(self, key):
        idx = self.array_type.flatten_index(key)
        return self.elements[idx].value


class RecordCellCluster:
    pass
