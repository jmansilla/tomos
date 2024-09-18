class State:
    def __init__(self):
        self.stack = {}
        self.stack_types = {}
        self.heap = {}


class EvalVisitor:

    def visit(self, expr, state):
        return expr.eval(state)


class Inspectable:
    def __init__(self):
        self.timeline = []
        self.by_name = {}

    def register_snapshot(self, expr, data, name=None):
        from copy import deepcopy
        new_snapshot = deepcopy(data)
        self.timeline.append(new_snapshot)
        if name is not None:
            assert name not in self.by_name
            self.by_name[name] = new_snapshot


class NaiveLinearInterpreter(Inspectable):
    """
    Linear interpreter. Knowns nothing about flow control.

    Assumes the code is a succession of expressions.
    Executes one expression after the other in sequential order.
    """
    def __init__(self, ast):
        super().__init__()
        self.ast = ast
        self.state = State()

    def get_entry_point(self):
        assert hasattr(self.ast, "body")
        return self.ast.body  # abstraction broken here. Shall not be a list

    def eval(self):
        self.finished = False
        ev = EvalVisitor()
        self.register_snapshot(None, self.state, name="initial")
        for instruction in self.get_entry_point():
            self.register_snapshot(instruction, self.state)
            self.state = ev.visit(instruction, self.state)
        self.register_snapshot(None, self.state, name="final")
        return self.state
