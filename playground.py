from prettytable import PrettyTable


class ShowState:

    def __init__(self, filename):
        self.filename = filename

    def __call__(self, last_sentence, state, next_sentence):
        with open(self.filename, 'w') as f:
            table = PrettyTable(['Name', 'Type', 'Value'])
            for name, cell in state.list_declared_variables().items():
                value = state.get_static_variable_value(name)
                table.add_row([name, cell, value])
            print(table, file=f)


def wait_for_input(*args):
    input("[Press Enter]... ")


if __name__ == "__main__":
    import sys
    from tomos.ayed2.parser import parser
    from tomos.ayed2.evaluation.interpreter import Interpreter

    source = sys.argv[1]
    ast = parser.parse(open(source).read())
    print(ast.pretty())

    interpreter = Interpreter(ast, hooks=[ShowState('state.mem'), wait_for_input])
    # print(interpreter.next_expr)
    result = interpreter.run()
    print(result)


