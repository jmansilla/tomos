from copy import deepcopy
from tomos.ayed2.evaluation.state import State
from tomos.ayed2.ast.types import IntType, RealType, BoolType
from tomos.visit import NodeVisitor


class EvaluationError(Exception):
    pass


class ExpressionsEvaluatorVisitor(NodeVisitor):

    def eval(self, expr, state):
        return self.visit(expr, state=state)

    def visit_boolean_constant(self, expr, **kw):
        if expr.value_str in BoolType.NAMED_CONSTANTS:
            return BoolType.NAMED_CONSTANTS[expr.value_str]
        else:
            raise EvaluationError(f"Invalid boolean value {expr.value_str}")

    def visit_integer_constant(self, expr, **kw):
        raw = expr.value_str
        if raw in IntType.NAMED_CONSTANTS:
            return IntType.NAMED_CONSTANTS[raw]
        try:
            return int(raw)
        except ValueError:
            raise EvaluationError(f"Invalid integer value {expr.value_str}")

    def visit_real_constant(self, expr, **kw):
        raw = expr.value_str
        if raw in RealType.NAMED_CONSTANTS:
            return RealType.NAMED_CONSTANTS[raw]
        try:
            return float(raw)
        except ValueError:
            raise EvaluationError(f"Invalid real value {expr.value_str}")

    def visit_unary_op(self, expr, **kw):
        children = kw["children"]
        assert len(children) == 1
        sub_value = children[0]
        if expr.op == "-":
            return -sub_value
        if expr.op == "+":
            return +sub_value
        elif expr.op == "!":
            return not sub_value
        else:
            raise EvaluationError(f"Invalid unary operator {expr.op}")

    def visit_binary_op(self, expr, **kw):
        children = kw["children"]
        assert len(children) == 2
        left = children[0]
        right = children[1]
        if expr.op == "+":
            return left + right
        if expr.op == "-":
            return left - right
        if expr.op == "*":
            return left * right
        if expr.op == "/":
            return left / right
        if expr.op == "%":
            return left % right
        if expr.op == "||":
            return left or right
        if expr.op == "&&":
            return left and right
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        raise EvaluationError(f"Invalid binary operator {expr.op}")

    def visit_variable(self, expr, **kw):
        state = kw["state"]
        return state.get_static_variable_value(expr.name)


class Inspectable:
    def __init__(self):
        self.timeline = []
        self.by_name = {}

    def register_snapshot(self, expr, data, name=None):
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
        return self.ast.body  # abstraction broken here. Shall not be a list

    def eval(self):
        self.finished = False
        ev = EvalVisitor()
        self.register_snapshot(None, self.state, name="initial")
        for instruction in self.get_entry_point():
            self.register_snapshot(instruction, self.state)
            self.state = ev.visit(instruction, self.state)
        self.register_snapshot(None, self.state, name="final")
        return self.state
