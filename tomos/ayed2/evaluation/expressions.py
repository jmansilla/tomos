from tomos.ayed2.ast.types import IntType, RealType, BoolType, CharType
from tomos.visit import NodeVisitor


class ExpressionEvaluationError(Exception):
    pass


class ExpressionEvaluator(NodeVisitor):

    def eval(self, expr, state):
        return self.visit(expr, state=state)

    def visit_boolean_constant(self, expr, **kw):
        if expr.value_str in BoolType.NAMED_CONSTANTS:
            return BoolType.NAMED_CONSTANTS[expr.value_str]
        else:
            raise ExpressionEvaluationError(f"Invalid boolean value {expr.value_str}")

    def visit_char_constant(self, expr, **kw):
        raw = expr.value_str
        if raw in CharType.NAMED_CONSTANTS:
            return CharType.NAMED_CONSTANTS[raw]
        if CharType.is_valid_value(raw):
            return raw
        raise ExpressionEvaluationError(f"Invalid char value \"{expr.value_str}\"")

    def visit_integer_constant(self, expr, **kw):
        raw = expr.value_str
        if raw in IntType.NAMED_CONSTANTS:
            return IntType.NAMED_CONSTANTS[raw]
        try:
            return int(raw)
        except ValueError:
            raise ExpressionEvaluationError(f"Invalid integer value {expr.value_str}")

    def visit_real_constant(self, expr, **kw):
        raw = expr.value_str
        if raw in RealType.NAMED_CONSTANTS:
            return RealType.NAMED_CONSTANTS[raw]
        try:
            return float(raw)
        except ValueError:
            raise ExpressionEvaluationError(f"Invalid real value {expr.value_str}")

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
            raise ExpressionEvaluationError(f"Invalid unary operator {expr.op}")

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
        raise ExpressionEvaluationError(f"Invalid binary operator {expr.op}")

    def visit_variable(self, expr, **kw):
        state = kw["state"]
        return state.get_static_variable_value(expr.name, expr._address_of, expr._dereferenced)
