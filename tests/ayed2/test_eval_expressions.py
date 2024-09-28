from unittest import TestCase

from tomos.ayed2.ast.types import IntType, BoolType, PointerOf
from tomos.ayed2.evaluation.state import UnkownValue, MemoryAddress
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator

from .factories.state import StateFactory
from .factories.expressions import (
    IntegerConstantFactory,
    BooleanConstantFactory,
    RealConstantFactory,
    VariableFactory,
    UnaryOpFactory,
    BinaryOpFactory,
)


def run_eval(expr, state=None):
    if state is None:
        state = StateFactory()
    evaluator = ExpressionEvaluator()
    return evaluator.eval(expr, state)


class TestEvalConstantExpressions(TestCase):

    def test_eval_integer_constant(self):
        expr = IntegerConstantFactory(token__value="5")
        self.assertEqual(run_eval(expr), 5)

    def test_eval_integer_inf(self):
        expr = IntegerConstantFactory(token__value="inf")
        self.assertEqual(run_eval(expr), float("inf"))

    def test_invalid_integer_constant_raises_exception(self):
        for value in ["5.5", "one", "null", "true", "false"]:
            expr = IntegerConstantFactory(token__value=value)
            with self.assertRaises(Exception):
                run_eval(expr)

    def test_eval_boolean_constant(self):
        expr = BooleanConstantFactory(token__value="true")
        self.assertEqual(run_eval(expr), True)
        expr = BooleanConstantFactory(token__value="false")
        self.assertEqual(run_eval(expr), False)

    def test_invalid_boolean_constant_raises_exception(self):
        for value in ["5", "5.5", "one", "null"]:
            expr = BooleanConstantFactory(token__value=value)
            with self.assertRaises(Exception):
                run_eval(expr)

    def test_eval_real_constant(self):
        expr = RealConstantFactory(token__value="5.5")
        self.assertEqual(run_eval(expr), 5.5)

    def test_eval_real_inf(self):
        expr = RealConstantFactory(token__value="inf")
        self.assertEqual(run_eval(expr), float("inf"))

    def test_invalid_real_constant_raises_exception(self):
        for value in [" ", "one", "null", "true", "false"]:
            expr = RealConstantFactory(token__value=value)
            with self.assertRaises(Exception):
                run_eval(expr)


class TestEvalVariableExpressions(TestCase):
    def test_eval_variable(self):
        name = "somename"
        expr = VariableFactory(name_token__value=name)
        state = StateFactory()
        state.declare_static_variable(name, IntType)
        state.set_static_variable_value(name, 5)
        self.assertEqual(run_eval(expr, state), 5)

    def test_undeclared_variable_raises_exception(self):
        expr = VariableFactory()
        state = StateFactory()
        with self.assertRaises(Exception):
            run_eval(expr, state)

    def test_declared_but_unset_variable_returns_unkown(self):
        var_expr = VariableFactory()
        state = StateFactory()
        state.declare_static_variable(var_expr.name, IntType)
        self.assertEqual(run_eval(var_expr, state), UnkownValue)

    def test_eval_variable_address(self):
        var_expr = VariableFactory()
        var_expr.address_of = True
        state = StateFactory()
        state.declare_static_variable(var_expr.name, IntType)
        state.set_static_variable_value(var_expr.name, 5)
        value = run_eval(var_expr, state)
        self.assertIsInstance(value, MemoryAddress)

    def test_eval_pointer_variable(self):
        var_a = VariableFactory()
        var_pointer_to_a = VariableFactory()
        state = StateFactory()
        state.declare_static_variable(var_a.name, IntType)
        some_value = 9
        state.set_static_variable_value(var_a.name, some_value)
        var_a_address = state.get_static_variable_value(var_a.name, address_of=True)

        state.declare_static_variable(var_pointer_to_a.name, PointerOf(of=IntType))
        state.set_static_variable_value(var_pointer_to_a.name, var_a_address)
        self.assertEqual(run_eval(var_pointer_to_a, state), var_a_address)
        var_pointer_to_a.dereferenced = True
        self.assertEqual(run_eval(var_pointer_to_a, state), some_value)

class TestEvalUnaryExpressions(TestCase):
    def test_eval_negative_integer(self):
        sub_expr = IntegerConstantFactory()
        expr = UnaryOpFactory(op_token__value="-", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), -1 * sub_val)

    def test_eval_positive_integer(self):
        sub_expr = IntegerConstantFactory()
        expr = UnaryOpFactory(op_token__value="+", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), sub_val)

    def test_eval_negative_real(self):
        sub_expr = RealConstantFactory()
        expr = UnaryOpFactory(op_token__value="-", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), -1 * sub_val)

    def test_eval_positive_real(self):
        sub_expr = RealConstantFactory()
        expr = UnaryOpFactory(op_token__value="+", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), sub_val)

    def test_eval_not_boolean(self):
        for value in BoolType.NAMED_CONSTANTS.keys():
            sub_expr = BooleanConstantFactory(token__value=value)
            expr = UnaryOpFactory(op_token__value="!", expr=sub_expr)
            sub_val = run_eval(sub_expr)
            self.assertEqual(run_eval(expr), not sub_val)


class TestEvalBinaryExpressions(TestCase):
    def test_adding_integers(self):
        a = IntegerConstantFactory(token__value="5")
        b = IntegerConstantFactory(token__value="5")
        expr = BinaryOpFactory(op_token__value="+", left_expr=a, right_expr=b)
        self.assertEqual(run_eval(expr), 10)
