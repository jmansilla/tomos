from tomos.ayed2.ast.types import ArrayOf, Tuple
from tomos.ayed2.evaluation.unknown_value import UnknownValue


class MemoryAllocator:
    def __init__(self):
        self.next_free_address = dict(
            [(partition, 0) for partition in MemoryAddress.PARTITIONS]
        )

    def allocate(self, partition, var_type):
        assert partition in MemoryAddress.PARTITIONS
        if isinstance(var_type, ArrayOf):
            elements = []
            for _ in range(var_type.number_of_elements()):
                elements.append(self.allocate(partition, var_type.of))
            return ArrayCellCluster(var_type, elements)
        elif isinstance(var_type, Tuple):
            sub_cells = {}
            for field_name, field_type in var_type.fields_mapping.items():
                sub_cells[field_name] = self.allocate(partition, field_type)
            return TupleCellCluster(var_type, sub_cells)
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

    def __lt__(self, other):
        if self.partition != other.partition:
            return self.partition < other.partition
        return self.address < other.address

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.partition, self.address))


class MemoryCell:
    can_get_set_values_directly = True
    cell_count = 1

    def __init__(self, address, var_type, value=None):
        assert isinstance(address, MemoryAddress)
        self.address = address
        self.var_type = var_type
        if value is None:
            self.value = UnknownValue
        else:
            self.value = value

    def __repr__(self):
        return f"MemoryCell({self.address}, {self.var_type}, value={self.value})"


class ArrayCellCluster:
    can_get_set_values_directly = False

    def __init__(self, array_type, elements):
        assert isinstance(array_type, ArrayOf)
        self.array_type = array_type
        self.elements = elements

    def __repr__(self):
        return f"ArrayCellCluster({self.array_type}, {self.elements})"

    @property
    def var_type(self):
        return self.array_type

    @property
    def address(self):
        return self.elements[0].address

    @property
    def cell_count(self):
        return sum(cell.cell_count for cell in self.elements)

    @property
    def value(self):
        # used by the UIs. Because of that, only importing here
        from functools import reduce
        from operator import mul

        def reshape(lst, shape):
            if len(shape) == 1:
                return lst
            n = reduce(mul, shape[1:])
            return [reshape(lst[i*n:(i+1)*n], shape[1:]) for i in range(len(lst)//n)]

        values = [cell.value for cell in self.elements]
        needed_shape = self.array_type.shape()
        return reshape(values, needed_shape)

    def __getitem__(self, key):
        idx = self.array_type.flatten_index(key)
        return self.elements[idx]


class TupleCellCluster:
    can_set_get_values_directly = False

    def __init__(self, tuple_type, sub_cells):
        assert isinstance(tuple_type, Tuple)
        self.tuple_type = tuple_type
        self.sub_cells = sub_cells

    @property
    def address(self):
        # used by the UIs
        if not hasattr(self, "_address"):
            self._address = min(sc.address for sc in self.sub_cells.values())
        return self._address

    @property
    def cell_count(self):
        return sum(cell.cell_count for cell in self.sub_cells.values())
