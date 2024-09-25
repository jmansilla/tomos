from prettytable import PrettyTable

from tomos.ayed2.ast.types import PointerOf, CharType
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
            for name, cell in state.list_declared_variables().items():
                cell = state.cell_by_names[name]
                value = cell.value
                if isinstance(cell.var_type, CharType) and not value == UnkownValue:
                    value = f"'{value}'"
                row = [name, cell.var_type, cell.var_type.SIZE, cell.address, value, '']

                if isinstance(cell.var_type, PointerOf):
                    referenced_cell = state.memory_cells.get(cell.value, None)
                    if referenced_cell is not None:
                        ref_value = referenced_cell.value
                        if isinstance(referenced_cell.var_type, CharType) and not ref_value == UnkownValue:
                            ref_value = f"'{ref_value}'"
                        row[-1] = ref_value
                table.add_row(row)
            table._dividers[-1] = True
            for cell in state.heap.values():
                table.add_row(['', cell.var_type, cell.var_type.SIZE, cell.address, cell.value, ''])
            print(table, file=f)
