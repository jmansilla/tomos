from unittest import TestCase
from unittest.mock import patch

from tomos.ayed2.parser import parser
from tomos.ayed2.parser.reserved_words import KEYWORDS
from tomos.ayed2.ast.expressions import (
    Expr,
    _Literal,
    Variable,
    IntegerLiteral,
    NullLiteral,
    EnumLiteral,
    CharLiteral,
)
from tomos.ayed2.ast.operators import UnaryOp
from tomos.ayed2.ast.program import Program, VarDeclaration
from tomos.ayed2.ast.sentences import Sentence, Assignment, If
from tomos.ayed2.ast.types import (
    IntType,
    BoolType,
    RealType,
    CharType,
    ArrayAxis,
    ArrayOf,
    PointerOf,
    Synonym,
    type_registry,
    Enum,
    Tuple,
)
from tomos.exceptions import TomosTypeError

from .factories.expressions import IntegerLiteralFactory


def compare_literals_for_testing(lit1, lit2):
    # Ignores the fact that they are different objects
    # and that the actual tokens may differ
    if type(lit1) != type(lit2):
        return False
    return lit1.value_str == lit2.value_str


def get_parsed_sentences(source, single_sentence=False, reset_registry=False):
    if reset_registry:
        type_registry.reset()
    if not source.endswith(";"):
        source = source + ";"
    program = parser.parse(source)
    if single_sentence:
        return next(iter(program.body))  # type: ignore
    return [s for s in program.body]  # type: ignore


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
        self.assertEqual(sent.name, "x")  # type: ignore
        self.assertIsInstance(sent.expr, Expr)  # type: ignore

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

    def test_variable_names_cant_be_keywords(self):
        for keyword in KEYWORDS:
            source = f"var {keyword}: int"
            self.assertRaises(TomosTypeError, get_parsed_sentences, source)


@patch("tomos.ayed2.ast.expressions._Literal.__eq__", new=compare_literals_for_testing)
class TestParseExpressions(TestCase):
    # Syntax does not permit an expression to be defined with no usage.
    # Thus, tests will do assignments, and we'll check properties on
    # the assigned-expression

    def parsed_expr(self, source):
        # here we'll add "x := " to what we receive as the expression source
        if ":=" not in source:
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
                expr, f"BinaryOp(IntegerLiteral(1), {symbol}, IntegerLiteral(2))"
            )

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
        var = expr
        self.assertEqual(var.name, "y")
        self.assertEqual(len(var.traverse_path), 1)
        self.assertEqual(var.traverse_path[0].kind, Variable.DEREFERENCE)

    def test_parse_dereferenced_negated(self):
        source = "-*y"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "-")
        self.assertIsInstance(expr.expr, Variable)
        var = expr.expr
        self.assertEqual(var.name, "y")
        self.assertEqual(len(var.traverse_path), 1)
        self.assertEqual(var.traverse_path[0].kind, Variable.DEREFERENCE)

    def test_parse_array_indexing_simple(self):
        IL = lambda x: IntegerLiteralFactory(token__value=str(x))
        source = "x[1]"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, Variable)
        var = expr
        self.assertEqual(var.name, "x")
        self.assertEqual(len(var.traverse_path), 1)
        step = var.traverse_path[0]
        self.assertEqual(step.kind, Variable.ARRAY_INDEXING)
        self.assertListEqual(step.argument, [IL(1)])

    def test_parse_array_indexing_multiple(self):
        IL = lambda x: IntegerLiteralFactory(token__value=str(x))
        source = "x[1, 5, 18, 6, 0]"
        expr = self.parsed_expr(source)
        self.assertIsInstance(expr, Variable)
        var = expr
        self.assertEqual(var.name, "x")
        self.assertEqual(len(var.traverse_path), 1)
        step = var.traverse_path[0]
        self.assertEqual(step.kind, Variable.ARRAY_INDEXING)
        self.assertListEqual(step.argument, [IL(1), IL(5), IL(18), IL(6), IL(0)])

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

    def test_parse_variable_modifiers_precedence(self):
        AI, AF, D = Variable.ARRAY_INDEXING, Variable.ACCESSED_FIELD, Variable.DEREFERENCE
        for source, expected_kinds in [
            ("*x.field_x[1]", [D, AF, AI]),
            ("*x.field_x[1].field_z", [D, AF, AI, AF]),
            ("*x.field_x[1][2][3]", [D, AF, AI, AI, AI]),
            ("(*x.field_x)[1]", [D, AF, AI]),
            ("*(x.field_x)[1]", [AF, D, AI]),
            ("*x.field_x", [D, AF]),
            ("x->field_x", [D, AF]),
            ("x->field_x[4]", [D, AF, AI]),
            ("**x", [D, D]),
        ]:
            expr = self.parsed_expr(source)
            self.assertIsInstance(expr, Variable)
            var = expr
            self.assertEqual(var.name, "x")
            self.assertEqual(len(var.traverse_path), len(expected_kinds))
            kinds = [step.kind for step in var.traverse_path]
            print("testing for", source)
            self.assertListEqual(kinds, expected_kinds)


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


class TestParsePointerVarDeclarations(TestCase):

    def test_parse_pointer_of_basic(self):
        source = "var x: pointer of int"
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, VarDeclaration)
        self.assertEqual(sent.name, "x")  # type: ignore
        self.assertIsInstance(sent.var_type, PointerOf)  # type: ignore
        self.assertIsInstance(sent.var_type.of, IntType)  # type: ignore

    def test_parse_pointer_of_pointer(self):
        source = "var x: pointer of pointer of int"
        sent = get_parsed_sentences(source, single_sentence=True)
        self.assertIsInstance(sent, VarDeclaration)
        self.assertEqual(sent.name, "x")  # type: ignore
        self.assertIsInstance(sent.var_type, PointerOf)  # type: ignore
        self.assertIsInstance(sent.var_type.of, PointerOf)  # type: ignore
        self.assertIsInstance(sent.var_type.of.of, IntType)  # type: ignore


class TestParseArrayVarDeclarations(TestCase):

    def test_parse_array_axes(self):
        for declaration, expectation in [
            ["array [10] of int", (ArrayAxis(0, 10),)],
            ["array [4..10] of int", (ArrayAxis(4, 10),)],
            ["array [4] of int", (ArrayAxis(0, 4),)],
            [
                "array [4, 10] of int",
                (
                    ArrayAxis(0, 4),
                    ArrayAxis(0, 10),
                ),
            ],
            [
                "array [4, 10, 4, 10] of int",
                (
                    ArrayAxis(0, 4),
                    ArrayAxis(0, 10),
                    ArrayAxis(0, 4),
                    ArrayAxis(0, 10),
                ),
            ],
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


class TestParseTypeDeclarationsSynonyms(TestCase):
    def test_parse_simple_synonym_declarations(self):
        new_type = "somenewtype"
        var_name = "x"
        for usual_type_name, var_type in [
            ("int", IntType),
            ("bool", BoolType),
            ("real", RealType),
            ("char", CharType),
        ]:
            source = f"type {new_type} = {usual_type_name}; var {var_name}: {new_type}"
            sentences = get_parsed_sentences(source, reset_registry=True)
            self.assertEqual(len(sentences), 1)
            sent = sentences[0]
            self.assertIsInstance(sent, VarDeclaration)
            self.assertIsInstance(sent.var_type, Synonym)

    def test_parse_synonym_of_pointer(self):
        new_type = "somenewtype"

        for usual_type_name, var_type in [
            ("int", IntType),
            ("bool", BoolType),
            ("real", RealType),
            ("char", CharType),
        ]:
            source = f"type {new_type} = pointer of {usual_type_name}; var x: {new_type}"
            sentences = get_parsed_sentences(source, reset_registry=True)
            self.assertEqual(len(sentences), 1)
            sent = sentences[0]
            self.assertIsInstance(sent, VarDeclaration)
            self.assertIsInstance(sent.var_type, Synonym)

    def test_declaring_var_of_unknown_type_should_fail(self):
        source = "var x: unknown"
        self.assertRaises(TomosTypeError, get_parsed_sentences, source)

    def test_overloading_existent_name_should_fail(self):
        source = "type int = int"
        self.assertRaises(TomosTypeError, get_parsed_sentences, source)
        source = "type new_type_name = int; type new_type_name = char"
        self.assertRaises(TomosTypeError, get_parsed_sentences, source)

    def test_cant_name_type_with_keyword(self):
        for keyword in KEYWORDS:
            source = f"type {keyword} = int"
            self.assertRaises(TomosTypeError, get_parsed_sentences, source)


class TestParseEnum(TestCase):
    def setUp(self):
        return type_registry.reset()

    def test_parse_simple_synonym_declarations(self):
        new_type = "somenewtype"
        var_name = "x"
        source = f"type {new_type} = enumerate Uno Dos Tres end enumerate; "
        source += f"var {var_name}: {new_type};"
        source += f" {var_name} := Uno;"
        sentences = get_parsed_sentences(source)
        self.assertEqual(
            len(sentences), 2
        )  # type declaration is sent to type_registry, and only 2 sents received
        var_dec_sent = sentences[0]
        self.assertIsInstance(var_dec_sent, VarDeclaration)
        self.assertIsInstance(var_dec_sent.var_type, Enum)
        assign_sent = sentences[1]
        self.assertIsInstance(assign_sent, Assignment)
        self.assertIsInstance(assign_sent.expr, EnumLiteral)


class TestParseTuple(TestCase):
    def setUp(self):
        return type_registry.reset()

    def test_parse_simple_tuple_declarations(self):
        new_type = "new_tuple"
        var_name = "x"
        source = f"type {new_type} = tuple field_a:int; field_b:char end tuple; "
        source += f"var {var_name}: {new_type};"
        source += f" {var_name}.field_a := 1;"
        source += f" {var_name}.field_b := 'B';"
        sentences = get_parsed_sentences(source)
        self.assertEqual(len(sentences), 3)
        var_dec_sent = sentences[0]
        self.assertIsInstance(var_dec_sent, VarDeclaration)
        self.assertIsInstance(var_dec_sent.var_type, Tuple)
        assign_sent = sentences[1]
        self.assertIsInstance(assign_sent, Assignment)
        self.assertIsInstance(assign_sent.expr, IntegerLiteral)
        assign_sent = sentences[2]
        self.assertIsInstance(assign_sent, Assignment)
        self.assertIsInstance(assign_sent.expr, CharLiteral)
