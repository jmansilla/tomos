class State:
    def __init__(self):
        self.stack = {}
        self.stack_types = {}
        self.heap = {}


class Inspectable:
    def __init__(self):
        self.timeline = []

    def register_snapshot(self, expr, snapshot):
        from copy import deepcopy
        self.timeline.append(deepcopy(snapshot))


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

    def eval(self):
        self.finished = False
        assert hasattr(self.ast, "body")
        for expr in self.ast.body:
            self.register_snapshot(expr, self.state)
            self.state = expr.eval(self.state)
        self.register_snapshot(None, self.state)
        return self.state