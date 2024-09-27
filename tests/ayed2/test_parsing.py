from unittest import TestCase

from tomos.ayed2.parser import parser
from tomos.ayed2.ast.expressions import Expr, _Constant, Variable, IntegerConstant
from tomos.ayed2.ast.operators import UnaryOp, BinaryOp
from tomos.ayed2.ast.program import Program, VarDeclaration
from tomos.ayed2.ast.sentences import Assignment
from tomos.ayed2.ast.types import IntType, BoolType, RealType, CharType


class TestParseProgram(TestCase):

    def test_parse_returns_program_object(self):
        source = "var x: int;"
        ast = parser.parse(source)
        self.assertIsInstance(ast, Program)


def get_parsed_sentences(source, single_sentence=False):
    if not source.endswith(";"):
        source = source + ";"
    program = parser.parse(source)
    if single_sentence:
        return next(iter(program.body))
    return [s for s in program.body]


class TestParseBasicTypeSentences(TestCase):
    def test_parse_var_declarations(self):
        for name, var_type in [
            ("int", IntType),
            ("bool", BoolType),
            ("real", RealType),
            ("char", CharType),
        ]:
            source = f"var x: {name}"
            sentences = get_parsed_sentences(source)
            self.assertEqual(len(sentences), 1)
            sent = sentences[0]
            self.assertIsInstance(sent, VarDeclaration)
            self.assertEqual(sent.name, "x")
            self.assertIsInstance(sent.var_type, var_type)

    def test_parse_assignments(self):
        source = "x := 1"
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, Assignment)
        self.assertEqual(sent.name, "x")
        self.assertIsInstance(sent.expr, Expr)

    def test_parse_literals(self):
        for value, var_type in [
            ("1", IntType),
            ("true", BoolType),
            ("1.0", RealType),
            ("'a'", CharType),
        ]:
            source = f"x := {value}"
            sent = get_parsed_sentences(source, single_sentence=True)
            self.assertIsInstance(sent, Assignment)
            self.assertIsInstance(sent.expr, _Constant)
            self.assertEqual(sent.expr._type, var_type)


class TestParseExpressions(TestCase):
    # Syntax does not permit an expression to be defined with no usage.
    # Thus, tests will do assignments, and we'll check properties on
    # the assigned-expression

    def parsed_expr(self, source):
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, Assignment)
        return sent.expr

    def test_parse_unary_ops_neg(self):
        source = "x := -1"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "-")
        self.assertIsInstance(expr.expr, _Constant)

    def test_parse_unary_ops_not(self):
        source = "x := !true"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "!")
        self.assertIsInstance(expr.expr, _Constant)

    def test_parse_numeric_binary_ops(self):
        for symbol in ["+", "*", "/", "%", "-", "<", "<=", ">", ">=", "==", "!="]:
            source = f"x := 1 {symbol} 2"
            expr = self.parsed_expr(source)
            self.assertIsInstance(expr, BinaryOp)
            self.assertEqual(expr.op, symbol)
            self.assertIsInstance(expr.left, _Constant)
            self.assertEqual(expr.left.value_str, "1")
            self.assertIsInstance(expr.right, _Constant)
            self.assertEqual(expr.right.value_str, "2")

    def test_parse_boolean_binary_ops(self):
        for symbol in ["||", "&&", "==", "!="]:
            source = f"x := true {symbol} false"
            expr = self.parsed_expr(source)
            self.assertIsInstance(expr, BinaryOp)
            self.assertEqual(expr.op, symbol)
            self.assertIsInstance(expr.left, _Constant)
            self.assertEqual(expr.left.value_str, "true")
            self.assertIsInstance(expr.right, _Constant)
            self.assertEqual(expr.right.value_str, "false")

    def test_parse_variable_expression(self):
        source = "x := y"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, Variable)
        self.assertEqual(expr.name, "y")

    def test_parse_dereferenced_variable_expression(self):
        source = "x := *y"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, Variable)
        self.assertEqual(expr.name, "y")
        self.assertEqual(expr._dereferenced, True)

    def test_parse_complex_expression(self):
        source = "x := 1 + 2 * 3"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "+")
        self.assertIsInstance(expr.left, IntegerConstant)
        self.assertEqual(expr.left.value_str, "1")
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, "*")
        self.assertIsInstance(expr.right.left, IntegerConstant)
        self.assertEqual(expr.right.left.value_str, "2")
        self.assertIsInstance(expr.right.right, IntegerConstant)
        self.assertEqual(expr.right.right.value_str, "3")
