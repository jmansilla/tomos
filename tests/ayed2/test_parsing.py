from unittest import TestCase

from tomos.ayed2.parser import parser
from tomos.ayed2.ast.expressions import Expr, _Literal, Variable, IntegerLiteral, NullLiteral
from tomos.ayed2.ast.operators import UnaryOp
from tomos.ayed2.ast.program import Program, VarDeclaration
from tomos.ayed2.ast.sentences import Sentence, Assignment, If
from tomos.ayed2.ast.types import IntType, BoolType, RealType, CharType, ArrayAxis, ArrayOf

from .factories.expressions import IntegerLiteralFactory


def get_parsed_sentences(source, single_sentence=False):
    if not source.endswith(";"):
        source = source + ";"
    program = parser.parse(source)
    if single_sentence:
        return next(iter(program.body))  # type: ignore
    return [s for s in program.body]     # type: ignore


class TestParseProgram(TestCase):

    def test_parse_returns_program_object(self):
        source = "var x: int;"
        ast = parser.parse(source)
        self.assertIsInstance(ast, Program)


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
        self.assertEqual(sent.name, "x")         # type: ignore
        self.assertIsInstance(sent.expr, Expr)   # type: ignore

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
            self.assertIsInstance(sent.expr, _Literal)  # type: ignore
            self.assertEqual(sent.expr._type, var_type)  # type: ignore

    def test_parse_infinity(self):
        source = "x := inf"
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, Assignment)
        self.assertIsInstance(sent.expr, IntegerLiteral)  # type: ignore
        self.assertEqual(sent.expr.value_str, "inf")  # type: ignore

    def test_parse_null(self):
        source = "x := null"
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, Assignment)
        self.assertIsInstance(sent.expr, NullLiteral)  # type: ignore
        self.assertEqual(sent.expr.value_str, "null")  # type: ignore


class TestParseExpressions(TestCase):
    # Syntax does not permit an expression to be defined with no usage.
    # Thus, tests will do assignments, and we'll check properties on
    # the assigned-expression

    def parsed_expr(self, source):
        # here we'll add "x := " to what we receive as the expression source
        if ':=' not in source:
            source = "x := " + source
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, Assignment)
        return sent.expr  # type: ignore

    def assertExpressionIs(self, expr, expected_str):
        self.assertIsInstance(expr, Expr)
        self.assertEqual(str(expr), expected_str)

    def assertExpressionEquals(self, expr1, expr2):
        self.assertEqual(str(expr1), str(expr2))

    def test_parse_unary_ops_neg(self):
        source = "-1"
        expr = self.parsed_expr(source)
        self.assertExpressionIs(expr, "UnaryOp(-, IntegerLiteral(1))")

    def test_parse_unary_ops_not(self):
        source = "!true"
        expr = self.parsed_expr(source)
        self.assertExpressionIs(expr, "UnaryOp(!, BooleanLiteral(true))")

    def test_parse_numeric_binary_ops(self):
        for symbol in ["+", "*", "/", "%", "-", "<", "<=", ">", ">=", "==", "!="]:
            source = f"1 {symbol} 2"
            expr = self.parsed_expr(source)
            self.assertExpressionIs(
                expr, f"BinaryOp(IntegerLiteral(1), {symbol}, IntegerLiteral(2))")

    def test_parse_boolean_binary_ops(self):
        for symbol in ["||", "&&", "==", "!="]:
            source = f"true {symbol} false"
            expr = self.parsed_expr(source)
            self.assertExpressionIs(
                expr,
                f"BinaryOp(BooleanLiteral(true), {symbol}, BooleanLiteral(false))",
            )

    def test_parse_variable_expression(self):
        source = "y"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, Variable)
        self.assertEqual(expr.name, "y")

    def test_parse_dereferenced_variable_expression(self):
        source = "*y"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, Variable)
        self.assertEqual(expr.name, "y")
        self.assertEqual(expr.dereferenced, True)

    def test_parse_dereferenced_negated(self):
        source = "-*y"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "-")
        self.assertIsInstance(expr.expr, Variable)
        self.assertEqual(expr.expr.name, "y")
        self.assertEqual(expr.expr.dereferenced, True)

    # Testing Operators Associativity and Precedence

    def test_precedence_order(self):
        source = "1 + 2 - 3 * 4 / 5 % 6 == 7"
        parenthesed = "((1 + 2) - (((3 * 4) / 5) % 6)) == 7"
        expr = self.parsed_expr(source)
        expected = self.parsed_expr(parenthesed)
        self.assertExpressionEquals(expr, expected)

    def test_parse_associativity_order(self):
        for source, parenthesed in [
            ("1 + 2 + 3", "(1 + 2) + 3"),
            ("1 - 2 - 3", "(1 - 2) - 3"),
            ("1 + 2 - 3", "(1 + 2) - 3"),
            ("1 - 2 + 3", "(1 - 2) + 3"),
            ("1 * 2 * 3", "(1 * 2) * 3"),
            ("1 / 2 / 3", "(1 / 2) / 3"),
            ("1 * 2 / 3", "(1 * 2) / 3"),
            ("1 / 2 * 3", "(1 / 2) * 3"),
            ("1 % 2 % 3", "(1 % 2) % 3"),
        ]:
            expr = self.parsed_expr(source)
            expected = self.parsed_expr(parenthesed)
            self.assertExpressionEquals(expr, expected)

    def test_parse_precedence(self):
        for source, parenthesed in [
            ("1 + 2 * 3", "1 + (2 * 3)"),
            ("1 - 2 * 3", "1 - (2 * 3)"),
            ("1 * 2 + 3", "(1 * 2) + 3"),
            ("1 * 2 - 3", "(1 * 2) - 3"),
            ("1 + 2 / 3", "1 + (2 / 3)"),
            ("1 - 2 / 3", "1 - (2 / 3)"),
            ("1 / 2 + 3", "(1 / 2) + 3"),
            ("1 / 2 - 3", "(1 / 2) - 3"),
        ]:
            expr = self.parsed_expr(source)
            expected = self.parsed_expr(parenthesed)
            self.assertExpressionEquals(expr, expected)


class TestParseIfSentences(TestCase):

    def parse(self, source):
        program = parser.parse(source)
        return next(iter(program.body))  # type: ignore

    def test_parse_if(self):
        source = """
        if true then
          x := 1
          else
          x := 2
          fi
        """
        sent = self.parse(source)
        self.assertIsInstance(sent, If)
        self.assertIsInstance(sent.guard, Expr)
        self.assertIsInstance(sent.then_sentences, list)
        for sub_sent in sent.then_sentences:
            self.assertIsInstance(sub_sent, Sentence)
        self.assertIsInstance(sent.else_sentences, list)
        for sub_sent in sent.else_sentences:
            self.assertIsInstance(sub_sent, Sentence)

    def test_parse_if_without_else(self):
        source = """
        if true then
          x := 1
          fi
        """
        sent = self.parse(source)
        self.assertIsInstance(sent, If)
        self.assertIsInstance(sent.guard, Expr)
        self.assertIsInstance(sent.then_sentences, list)
        for sub_sent in sent.then_sentences:
            self.assertIsInstance(sub_sent, Sentence)
        self.assertEqual(sent.else_sentences, [])

    def test_parse_several_sentences_in_if(self):
        source = """
        if true then
          x := 1
          y := 2
          z := 3
          fi
        """
        sent = self.parse(source)
        self.assertIsInstance(sent, If)
        self.assertIsInstance(sent.guard, Expr)
        self.assertIsInstance(sent.then_sentences, list)
        self.assertEqual(len(sent.then_sentences), 3)
        self.assertEqual(len(sent.else_sentences), 0)

    def test_parse_nested_ifs(self):
        source = """
        if x >= 0 then
            if x == 0 then
                y := 1
            else
                y := 2
            fi
        else  // x < 0
            if x >= -10 then
                y := 3
            else
                y := 4
            fi
        fi
        """
        sent = self.parse(source)
        self.assertIsInstance(sent, If)
        self.assertIsInstance(sent.guard, Expr)
        self.assertEqual(len(sent.then_sentences), 1)
        self.assertIsInstance(sent.then_sentences[0], If)
        self.assertEqual(len(sent.else_sentences), 1)
        self.assertIsInstance(sent.else_sentences[0], If)

    def test_parse_nested_ifs_parent_without_else(self):
        source = """
        if x >= 0 then
            if x == 0 then
                y := 1
            else
                y := 2
            fi
        fi
        """
        sent = self.parse(source)
        self.assertIsInstance(sent, If)
        self.assertIsInstance(sent.guard, Expr)
        self.assertEqual(len(sent.then_sentences), 1)
        self.assertIsInstance(sent.then_sentences[0], If)
        self.assertEqual(len(sent.else_sentences), 0)


class TestParseArrayVarDeclarations(TestCase):

    def test_parse_array_axes(self):
        IC = lambda x: IntegerLiteralFactory(token__value=str(x))
        IC10 = IC(10)
        IC4 = IC(4)
        for declaration, expectation in [
            ["array [10] of int", (ArrayAxis(0, IC10), )],
            ["array [4..10] of int", (ArrayAxis(IC4, IC10), )],
            ["array [4] of int", (ArrayAxis(0, IC4), )],
            ["array [4, 10] of int", (ArrayAxis(0, IC4), ArrayAxis(0, IC10), )],
            ["array [4, 10, 4, 10] of int",
                (ArrayAxis(0, IC4), ArrayAxis(0, IC10), ArrayAxis(0, IC4), ArrayAxis(0, IC10),)],
        ]:
            source = f"var x: {declaration}"
            sent = get_parsed_sentences(source, single_sentence=True)
            self.assertIsInstance(sent, VarDeclaration)
            self.assertIsInstance(sent.var_type, ArrayOf)  # type: ignore
            self.assertEqual(str(sent.var_type.axes), str(expectation))  # type: ignore

    def test_parse_var_declarations(self):
        for name, var_type in [
            ("int", IntType),
            ("bool", BoolType),
            ("real", RealType),
            ("char", CharType),
        ]:
            limit = 10
            source = f"var x: array [{limit}] of {name}"
            sentences = get_parsed_sentences(source)
            self.assertEqual(len(sentences), 1)
            sent = sentences[0]
            self.assertIsInstance(sent, VarDeclaration)
            self.assertEqual(sent.name, "x")
            self.assertIsInstance(sent.var_type.of, var_type)

    def test_array_of_array(self):
        source = "var x: array [10] of array [4] of int"
        sentences = get_parsed_sentences(source)
        self.assertEqual(len(sentences), 1)
        sent = sentences[0]
        self.assertIsInstance(sent, VarDeclaration)
        self.assertIsInstance(sent.var_type, ArrayOf)
        self.assertIsInstance(sent.var_type.of, ArrayOf)  # type: ignore
        self.assertIsInstance(sent.var_type.of.of, IntType)  # type: ignore

    def test_array_of_variable(self):
        source = "var x: array [N] of int"
        sentences = get_parsed_sentences(source)
        self.assertEqual(len(sentences), 1)
        sent = sentences[0]
        self.assertIsInstance(sent, VarDeclaration)
        self.assertIsInstance(sent.var_type, ArrayOf)
        self.assertEqual(str(sent.var_type.axes[0]), 'Axis(0, Variable(N))')
