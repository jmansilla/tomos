from tomos.ayed2.ast.types import ArrayOf
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
            self.value = UnknownValue
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
