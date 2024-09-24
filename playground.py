from prettytable import PrettyTable


class ShowState:

    def __init__(self, filename):
        self.filename = filename

    def __call__(self, last_sentence, state):
        from tomos.ayed2.ast.types import PointerOf
        with open(self.filename, 'w') as f:
            table = PrettyTable(['Name', 'Type', 'Size', 'Address', 'Value', 'Pointed value'])
            for name, cell in state.list_declared_variables().items():
                cell = state.cell_by_names[name]
                row = [name, cell.var_type, cell.var_type.SIZE, cell.address, cell.value, '']

                if isinstance(cell.var_type, PointerOf):
                    referenced_cell = state.memory_cells.get(cell.value, None)
                    if referenced_cell is not None:
                        row[-1] = referenced_cell.value
                table.add_row(row)
            for cell in state.heap.values():
                table.add_row(['', cell.var_type, cell.var_type.SIZE, cell.address, cell.value, ''])
            print(table, file=f)


def wait_for_input(*args):
    input("[Press Enter]... ")

class Sleeper:
    def __init__(self, delta) -> None:
        self.delta = delta

    def __call__(self, *args):
        from time import sleep
        sleep(self.delta)

class ShowSentence:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    def __init__(self, filename):
        self.filename = filename
        self.source_lines = open(filename).read().split('\n')


    def __call__(self, last_sentence, state, sentence_to_run):
        print(self.OKCYAN, sentence_to_run, self.ENDC)
        actual_line = self.source_lines[sentence_to_run.line_number - 1]
        print(self.OKBLUE, actual_line, self.ENDC)


if __name__ == "__main__":
    import sys
    from tomos.ayed2.parser import parser
    from tomos.ayed2.evaluation.interpreter import Interpreter

    source = sys.argv[1]
    ast = parser.parse(open(source).read())
    print(ast.pretty())

    interpreter = Interpreter(ast, pre_hooks=[ShowSentence(source), wait_for_input, ],
                              post_hooks=[ShowState('state.mem'), ])
    if "--run" in sys.argv:
        result = interpreter.run()
        print(result)
    elif "-i" in sys.argv:
        print (sys.argv)
        import ipdb; ipdb.set_trace()


