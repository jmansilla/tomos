from unittest import TestCase

from tomos.ayed2.ast.types import IntType, BoolType, RealType, CharType, PointerOf, Synonym
from tomos.ayed2.evaluation.state import State, UnknownValue, MemoryAddress
from tomos.exceptions import AlreadyDeclaredVariableError, MemoryInfrigementError, TomosTypeError, UndeclaredVariableError
from .factories.expressions import VariableFactory


def Var(name):
    return VariableFactory(name_token__value=name)


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
        var = Var("x")
        state.set_variable_value(var, 5)
        self.assertEqual(state.get_variable_value(var), 5)

    def test_set_variable_of_wrong_type_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(TomosTypeError):
            state.set_variable_value(Var("x"), True)

    def test_set_variable_before_declaration_raises_exception(self):
        state = State()
        with self.assertRaises(UndeclaredVariableError):
            state.set_variable_value(Var("x"), 5)

    def test_get_variable_after_declaration_returns_unknown(self):
        state = State()
        state.declare_static_variable("x", IntType)
        self.assertEqual(state.get_variable_value(Var("x")), UnknownValue)


class TestEvalStateAllocFree(TestCase):

    def test_alloc_for_pointer_variable(self):
        for base_type_class in [IntType, BoolType, RealType, CharType]:
            state = State()
            base_type = base_type_class()
            state.declare_static_variable("x", PointerOf(base_type))
            var = Var("x")
            self.assertEqual(state.get_variable_value(var), UnknownValue)
            state.alloc(var)
            # now shall have an address as value
            value = state.get_variable_value(var)
            self.assertNotEqual(value, UnknownValue)
            self.assertIsInstance(value, MemoryAddress)
            self.assertEqual(state.heap[value].var_type, base_type)

    def test_doing_alloc_for_not_pointer_variable_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(TomosTypeError):
            state.alloc(Var("x"))

    def test_doing_free_for_not_pointer_variable_raises_exception(self):
        state = State()
        state.declare_static_variable("x", IntType)
        with self.assertRaises(TomosTypeError):
            state.free(Var("x"))

    def test_free_for_pointer_variable(self):
        state = State()
        state.declare_static_variable("x", PointerOf(IntType()))
        var = Var("x")
        state.alloc(var)
        value = state.get_variable_value(var)
        state.free(var)
        self.assertEqual(state.get_variable_value(var), UnknownValue)
        self.assertNotIn(value, state.heap)

    def test_free_twice_raises_exception(self):
        state = State()
        state.declare_static_variable("x", PointerOf(IntType()))
        var = Var("x")
        state.alloc(var)
        state.free(var)
        with self.assertRaises(MemoryInfrigementError):
            state.free(var)

    def test_alloc_free_for_not_declared_variable_raises_exception(self):
        state = State()
        with self.assertRaises(UndeclaredVariableError):
            state.alloc(Var("y"))
        with self.assertRaises(UndeclaredVariableError):
            state.free(Var("y"))


class TestEvalStateForSynonyms(TestCase):

    def test_declare_var_synonym_of_int(self):
        numberType = Synonym(IntType())
        state = State()
        state.declare_static_variable("x", numberType)
        var = Var("x")
        state.set_variable_value(var, 5)
        self.assertRaises(Exception, state.set_variable_value, var, "c")

    def test_alloc_free_for_synonym_pointer_variable(self):
        int_type = IntType()
        numberType = Synonym(int_type)
        state = State()
        state.declare_static_variable("x", PointerOf(numberType))
        var = Var("x")
        self.assertEqual(state.get_variable_value(var), UnknownValue)
        state.alloc(var)
        value = state.get_variable_value(var)
        self.assertNotEqual(value, UnknownValue)
        self.assertIsInstance(value, MemoryAddress)
        self.assertEqual(state.heap[value].var_type, int_type)  # the underlying type
        state.free(var)
        self.assertEqual(state.get_variable_value(var), UnknownValue)
        self.assertNotIn(value, state.heap)

