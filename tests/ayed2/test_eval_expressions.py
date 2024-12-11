from unittest import TestCase

from tomos.ayed2.ast.types import IntType, BoolType, PointerOf
from tomos.ayed2.evaluation.state import UnknownValue, MemoryAddress
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator

from .factories.state import StateFactory
from .factories.expressions import (
    IntegerLiteralFactory,
    BooleanLiteralFactory,
    RealLiteralFactory,
    VariableFactory,
    UnaryOpFactory,
    BinaryOpFactory,
)


def run_eval(expr, state=None):
    if state is None:
        state = StateFactory()
    evaluator = ExpressionEvaluator()
    return evaluator.eval(expr, state)


class TestEvalLiteralExpressions(TestCase):

    def test_eval_integer_literal(self):
        expr = IntegerLiteralFactory(token__value="5")
        self.assertEqual(run_eval(expr), 5)

    def test_eval_integer_inf(self):
        expr = IntegerLiteralFactory(token__value="inf")
        self.assertEqual(run_eval(expr), float("inf"))

    def test_invalid_integer_literal_raises_exception(self):
        for value in ["5.5", "one", "null", "true", "false"]:
            expr = IntegerLiteralFactory(token__value=value)
            with self.assertRaises(Exception):
                run_eval(expr)

    def test_eval_boolean_literal(self):
        expr = BooleanLiteralFactory(token__value="true")
        self.assertEqual(run_eval(expr), True)
        expr = BooleanLiteralFactory(token__value="false")
        self.assertEqual(run_eval(expr), False)

    def test_invalid_boolean_literal_raises_exception(self):
        for value in ["5", "5.5", "one", "null"]:
            expr = BooleanLiteralFactory(token__value=value)
            with self.assertRaises(Exception):
                run_eval(expr)

    def test_eval_real_literal(self):
        expr = RealLiteralFactory(token__value="5.5")
        self.assertEqual(run_eval(expr), 5.5)

    def test_eval_real_inf(self):
        expr = RealLiteralFactory(token__value="inf")
        self.assertEqual(run_eval(expr), float("inf"))

    def test_invalid_real_literal_raises_exception(self):
        for value in [" ", "one", "null", "true", "false"]:
            expr = RealLiteralFactory(token__value=value)
            with self.assertRaises(Exception):
                run_eval(expr)


class TestEvalVariableExpressions(TestCase):
    def test_eval_variable(self):
        name = "somename"
        expr = VariableFactory(name_token__value=name)
        state = StateFactory()
        state.declare_static_variable(name, IntType)
        state.set_variable_value(name, 5)
        self.assertEqual(run_eval(expr, state), 5)

    def test_undeclared_variable_raises_exception(self):
        expr = VariableFactory()
        state = StateFactory()
        with self.assertRaises(Exception):
            run_eval(expr, state)

    def test_declared_but_unset_variable_returns_unknown(self):
        var_expr = VariableFactory()
        state = StateFactory()
        state.declare_static_variable(var_expr.name, IntType)
        self.assertEqual(run_eval(var_expr, state), UnknownValue)

    def test_eval_pointer_variable(self):
        var_pointer = VariableFactory()
        state = StateFactory()
        state.declare_static_variable(var_pointer.name, PointerOf(of=IntType))
        state.alloc(var_pointer.name)
        self.assertIsInstance(run_eval(var_pointer, state), MemoryAddress)
        var_pointer.dereferenced = True
        self.assertNotIsInstance(run_eval(var_pointer, state), MemoryAddress)


class TestEvalUnaryExpressions(TestCase):
    def test_eval_negative_integer(self):
        sub_expr = IntegerLiteralFactory()
        expr = UnaryOpFactory(op_token__value="-", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), -1 * sub_val)

    def test_eval_positive_integer(self):
        sub_expr = IntegerLiteralFactory()
        expr = UnaryOpFactory(op_token__value="+", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), sub_val)

    def test_eval_negative_real(self):
        sub_expr = RealLiteralFactory()
        expr = UnaryOpFactory(op_token__value="-", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), -1 * sub_val)

    def test_eval_positive_real(self):
        sub_expr = RealLiteralFactory()
        expr = UnaryOpFactory(op_token__value="+", expr=sub_expr)
        sub_val = run_eval(sub_expr)
        self.assertEqual(run_eval(expr), sub_val)

    def test_eval_not_boolean(self):
        for value in BoolType.NAMED_LITERALS.keys():
            sub_expr = BooleanLiteralFactory(token__value=value)
            expr = UnaryOpFactory(op_token__value="!", expr=sub_expr)
            sub_val = run_eval(sub_expr)
            self.assertEqual(run_eval(expr), not sub_val)


class TestEvalBinaryExpressions(TestCase):
    def test_adding_integers(self):
        a = IntegerLiteralFactory(token__value="5")
        b = IntegerLiteralFactory(token__value="5")
        expr = BinaryOpFactory(op_token__value="+", left_expr=a, right_expr=b)
        self.assertEqual(run_eval(expr), 10)
