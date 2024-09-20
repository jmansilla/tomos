from unittest import TestCase

from tomos.ayed2.ast.types import IntType, BoolType, RealType
from tomos.ayed2.evaluation.state import State, UnkownValue, Ayed2TypeError


class TestEvalState(TestCase):

    def test_created_state_is_empty(self):
        state = State()
        self.assertDictEqual(state.list_declared_variables(), {})

    def test_declare_variable(self):
        state = State()
        state.declare_static_variable("x", IntType)
        declareds = state.list_declared_variables()
        self.assertIn("x", declareds)
        self.assertEqual(declareds["x"], IntType)

    def test_redeclare_variable_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(Ayed2TypeError):
            state.declare_static_variable("x", BoolType)

    def test_set_variable(self):
        state = State()
        state.declare_static_variable("x", IntType)
        state.set_static_variable_value("x", 5, IntType)
        self.assertEqual(state.get_static_variable_value("x"), 5)

    def test_set_variable_of_wrong_type_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(Ayed2TypeError):
            state.set_static_variable_value("x", True, BoolType)

    def test_set_variable_before_declaration_raises_exception(self):
        state = State()
        with self.assertRaises(Ayed2TypeError):
            state.set_static_variable_value("x", 5, IntType)

    def test_get_variable_after_declaration_returns_unkown(self):
        state = State()
        state.declare_static_variable("x", IntType)
        self.assertEqual(state.get_static_variable_value("x"), UnkownValue)
