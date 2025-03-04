import pprint
from prettytable import PrettyTable

from tomos.ayed2.ast.types import ArrayOf, CharType
from tomos.ayed2.evaluation.state import UnknownValue
from tomos.ui.colors import bcolors


class ShowState:

    def __init__(self, filename, show_diff=True):
        self.filename = filename
        self.show_diff = show_diff
        self.differ = MemoryDiffer()

    def __call__(self, last_sentence, state, expression_values):
        table = PrettyTable(["Name", "Type", "Size", "Address", "Value", "Pointed value"])
        table.align["Name"] = "l"
        table.align["Type"] = "l"
        table.align["Value"] = "r"
        table.align["Pointed value"] = "r"
        for name, _ in state.list_declared_variables().items():
            cell = state.stack[name]
            table.add_row(self.build_cell_row(name, cell, state))

        table._dividers[-1] = True

        for cell in state.heap.values():
            table.add_row(self.build_cell_row(name="", cell=cell, state=state))
        self.dump_to_file(table)

    def dump_to_file(self, table):
        with open(self.filename, "w") as f:
            print(table, file=f)

    def build_cell_row(self, name, cell, state):
        fmt_value = self.formated_cell_value(cell)
        row = [name, cell.var_type, cell.var_type.SIZE, cell.address, fmt_value, ""]

        if cell.var_type.is_pointer:
            # pointers always point to a heap cell
            referenced_cell = state.heap.get(cell.value, None)
            if referenced_cell is not None:
                row[-1] = self.formated_cell_value(referenced_cell)

        return row

    def formated_cell_value(self, cell):
        if isinstance(cell.var_type, ArrayOf):
            value = self.format_array(cell)
        else:
            value = cell.value
            if isinstance(cell.var_type, CharType) and not value == UnknownValue:
                value = f"'{value}'"
            if self.show_diff:
                value = self.differ(cell.address, value)
        return value

    def format_array(self, cell):
        value = [self.formated_cell_value(sub_cell) for sub_cell in cell.elements]
        if len(cell.var_type.axes) == 2:
            # Matrix. Plot it accordling
            len_1 = cell.var_type.axes[0].length
            len_2 = cell.var_type.axes[1].length
            matrix = [value[i * len_2 : (i + 1) * len_2] for i in range(len_1)]
            value = pprint.pformat(matrix, width=40)

        return value


class MemoryDiffer:
    class Changed:
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return f"{bcolors.OKGREEN}{self.value}{bcolors.ENDC}"

    def __init__(self):
        self._previous_values = {}

    def __call__(self, key, value):
        if key in self._previous_values:
            previous_value = self._previous_values[key]
        else:
            previous_value = None
        self._previous_values[key] = value

        if previous_value is not None and previous_value != value:
            return self.Changed(value)
        else:
            return value
