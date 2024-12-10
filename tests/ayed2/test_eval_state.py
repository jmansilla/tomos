from unittest import TestCase

from tomos.ayed2.ast.types import IntType, BoolType, RealType, CharType, PointerOf
from tomos.ayed2.evaluation.state import State, UnknownValue, MemoryAddress
from tomos.exceptions import AlreadyDeclaredVariableError, MemoryInfrigementError, TomosTypeError, UndeclaredVariableError


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
        with self.assertRaises(AlreadyDeclaredVariableError):
            state.declare_static_variable("x", BoolType)

    def test_set_variable(self):
        state = State()
        state.declare_static_variable("x", IntType)
        state.set_variable_value("x", 5)
        self.assertEqual(state.get_variable_value("x"), 5)

    def test_set_variable_of_wrong_type_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(TomosTypeError):
            state.set_variable_value("x", True)

    def test_set_variable_before_declaration_raises_exception(self):
        state = State()
        with self.assertRaises(UndeclaredVariableError):
            state.set_variable_value("x", 5)

    def test_get_variable_after_declaration_returns_unknown(self):
        state = State()
        state.declare_static_variable("x", IntType)
        self.assertEqual(state.get_variable_value("x"), UnknownValue)


class TestEvalStateAllocFree(TestCase):

    def test_alloc_for_pointer_variable(self):
        for base_type in [IntType, BoolType, RealType, CharType]:
            state = State()
            state.declare_static_variable("x", PointerOf(base_type))
            self.assertEqual(state.get_variable_value("x"), UnknownValue)
            state.alloc("x")
            # now shall have an address as value
            value = state.get_variable_value("x")
            self.assertNotEqual(value, UnknownValue)
            self.assertIsInstance(value, MemoryAddress)
            self.assertEqual(state.heap[value].var_type, base_type)

    def test_doing_alloc_for_not_pointer_variable_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(TomosTypeError):
            state.alloc("x")

    def test_doing_free_for_not_pointer_variable_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(TomosTypeError):
            state.free("x")

    def test_free_for_pointer_variable(self):
        state = State()
        state.declare_static_variable("x", PointerOf(IntType))
        state.alloc("x")
        value = state.get_variable_value("x")
        state.free("x")
        self.assertEqual(state.get_variable_value("x"), UnknownValue)
        self.assertNotIn(value, state.heap)

    def test_free_twice_raises_exception(self):
        state = State()
        state.declare_static_variable("x", PointerOf(IntType))
        state.alloc("x")
        state.free("x")
        with self.assertRaises(MemoryInfrigementError):
            state.free("x")

    def test_alloc_free_for_not_declared_variable_raises_exception(self):
        state = State()
        with self.assertRaises(UndeclaredVariableError):
            state.alloc("y")
        with self.assertRaises(UndeclaredVariableError):
            state.free("y")
