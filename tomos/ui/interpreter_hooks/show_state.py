from prettytable import PrettyTable
import pprint

from tomos.ayed2.ast.types import ArrayOf, PointerOf, CharType
from tomos.ayed2.evaluation.state import UnkownValue


class ShowState:

    def __init__(self, filename):
        self.filename = filename

    def __call__(self, last_sentence, state):
        with open(self.filename, 'w') as f:
            table = PrettyTable(['Name', 'Type', 'Size', 'Address', 'Value', 'Pointed value'])
            table.align['Name'] = 'l'
            table.align['Type'] = 'l'
            table.align['Value'] = 'r'
            table.align['Pointed value'] = 'r'
            for name, _ in state.list_declared_variables().items():
                cell = state.cell_by_names[name]
                table.add_row(self.build_cell_row(name, cell, state))

            table._dividers[-1] = True

            for cell in state.heap.values():
                table.add_row(self.build_cell_row(name='', cell=cell, state=state))
            print(table, file=f)

    def build_cell_row(self, name, cell, state):
        fmt_value = self.formated_cell_value(cell)
        row = [name, cell.var_type, cell.var_type.SIZE, cell.address, fmt_value, '']

        if isinstance(cell.var_type, PointerOf):
            referenced_cell = state.memory_cells.get(cell.value, None)
            if referenced_cell is not None:
                row[-1] = self.formated_cell_value(referenced_cell)

        return row

    def formated_cell_value(self, cell):
        if isinstance(cell.var_type, ArrayOf):
            value = self.format_array(cell)
        else:
            value = cell.value
            if isinstance(cell.var_type, CharType) and not value == UnkownValue:
                value = f"'{value}'"
        return value

    def format_array(self, cell):
        value = [
            self.formated_cell_value(sub_cell)
            for sub_cell in cell.elements
        ]
        if len(cell.var_type.axes) == 2:
           # Matrix. Plot it accordling
           len_1 = cell.var_type.axes[0].length
           len_2 = cell.var_type.axes[1].length
           matrix = [
               value[i * len_2:(i + 1) * len_2]
               for i in range(len_1)
           ]
           value = pprint.pformat(matrix, width=40)

        return value
