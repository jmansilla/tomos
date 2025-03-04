import os

from lark import Transformer

from tomos.ayed2.ast.types import *
from tomos.ayed2.ast.expressions import *
from tomos.ayed2.ast.sentences import *
from tomos.ayed2.ast.operators import *
from tomos.ayed2.ast.program import *
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator
from tomos.ayed2.parser.token import Token
from tomos.exceptions import TomosTypeError, TomosSyntaxError


from .reserved_words import KEYWORDS


def chain_instructions(instructions):
    """Makes sure that next_instruction is set for each instruction"""
    prev = None
    for inst in instructions:
        if prev is not None:
            prev.next_instruction = inst
        prev = inst
    return instructions


class TreeToAST(Transformer):
    do_eval_literals = True

    def program(self, args):
        tdef, fdef, body = args
        return Program(
            typedef_section=chain_instructions(tdef.children),
            funprocdef_section=chain_instructions(fdef.children),
            body=body,
        )

    def sentences(self, args):
        sents = chain_instructions(list(args))
        return sents

    def body(self, args):
        vardef, sentences = args
        body = Body(var_declarations=vardef.children, sentences=sentences)
        chain_instructions(iter(body))
        return body

    def if_sent(self, args):
        if len(args) == 2:
            guard, then_sentences = args
            else_sentences = []
        else:
            guard, then_sentences, else_sentences = args
        return If(guard=guard, then_sentences=then_sentences, else_sentences=else_sentences)

    def while_sent(self, args):
        guard, sentences = args
        return While(guard=guard, sentences=sentences)

    def for_sent_up(self, args):
        return True, args

    def for_sent_down(self, args):
        return False, args

    def for_sent(self, children_responses):
        assert len(children_responses) == 1
        up, args = children_responses[0]
        var_token, start, end, sentences = args
        var = self.variable([var_token])
        return For(var, start, end, up, sentences)

    def SKIP(self, token):
        return Skip(token)

    def var_declaration(self, args):
        var, var_type = args
        if var.name in KEYWORDS:
            raise TomosTypeError(f"Cant use {var.name} as variable name because it is reserved")
        if var_type.is_deferred:
            var_type = var_type.resolve()
        elif var_type.has_deferrals():
            var_type = var_type.resolve_deferrals()
        return VarDeclaration(variable=var, var_type=var_type)

    def pointer_of(self, args):
        assert len(args) == 1
        pointed_type = args[0]
        return PointerOf(of=pointed_type)

    def type(self, args):
        # This production is used in several different places.
        # a) when declaring a variable of basic type
        # b) when declaring a variable of a custom-type
        # c) when declaring a variable of pointer type or array type
        #    (where "type" is an argument to the complex-type constructor)
        # d) when declaring a type synonym
        #
        assert len(args) == 1
        arg0 = args[0]
        if isinstance(arg0, Token):
            # we are in case a) b) or d) described above
            factory = type_registry.get_type_factory(arg0.value, deferred_if_not_found=True)
            if isinstance(factory, type_registry.Deferred):
                return factory  # it's a Deferred object. It's not resolved later, will blow up
            else:
                return factory()
        elif isinstance(arg0, Ayed2Type):
            # we are in case c)
            return arg0
        else:
            raise TomosSyntaxError(f"Invalid type {arg0}", guess_line_nr_from=arg0)

    def custom_type(self, args):
        assert len(args) == 1
        return args[0]

    def syn(self, args):
        # synomym for type
        assert len(args) == 1
        u_type = args[0]
        if isinstance(u_type, type_registry.Deferred):
            u_type = u_type.resolve()
        return Synonym(underlying_type=u_type)

    def enum(self, args):
        assert len(args) >= 1
        values = []
        for arg in args:
            if not isinstance(arg, Token):
                raise TomosSyntaxError(
                    f"Invalid enum literal {arg}. Expected token, got {type(arg)} instead.",
                    guess_line_nr_from=arg,
                )
            values.append(arg.value)
        return Enum(values)

    def tuple_field(self, args):
        assert len(args) == 2
        return (args[0], args[1])

    def fieldname(self, args):
        assert len(args) == 1
        return args[0]

    def t_tuple(self, args):
        assert len(args) >= 1
        fields_mapping = {}
        for arg in args:
            if not isinstance(arg, tuple):
                raise TomosSyntaxError(
                    f"Invalid tuple field {arg}. Expected tuple, got {type(arg)} instead.",
                    guess_line_nr_from=arg,
                )
            fields_mapping[arg[0]] = arg[1]
        return Tuple(fields_mapping=fields_mapping)

    def typedecl(self, args):
        assert len(args) == 2
        new_name, new_type = args
        if new_name in KEYWORDS:
            raise TomosTypeError(f"Type name {new_name} is reserved")
        type_registry.register_type(new_name, new_type)
        return TypeDeclaration(name=new_name, new_type=new_type)

    def builtin_name(self, args):
        token = args[0]
        return token

    def builtin_call(self, args):
        name, *call_args = args
        return BuiltinCall(name=name, args=call_args)

    def assignment(self, args):
        dest, expr = args
        return Assignment(dest_variable=dest, expr=expr)

    def expr_binary(self, args):
        # Encapsulates BinaryExpressions or higher in precedence
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            left, op, right = args
            return BinaryOp(left_expr=left, op_token=op, right_expr=right)
        elif len(args) > 3:
            # here we need to solve associativity
            left, op, right, *rest = args
            sub_expr = BinaryOp(left_expr=left, op_token=op, right_expr=right)
            return self.expr_binary([sub_expr] + rest)
        else:
            raise TomosSyntaxError(f"Invalid binary expression: {args}", guess_line_nr_from=args)

    expr_term = expr_binary
    expr_factor = expr_binary
    expr_comparison = expr_binary
    expr_equality = expr_binary
    expr_junction = expr_binary

    def expr_unary(self, args):
        # Unary encapsulates UnaryExpressions or higher in precedence
        if len(args) == 1:
            # it may be a literal or variable alone
            return args[0]
        elif len(args) == 2:
            op, expr = args
            return UnaryOp(op_token=op, expr=expr)
        return args

    def getenv(self, args):
        env_variable_name = args[0].value
        expected_type = args[1].value
        if env_variable_name not in os.environ:
            raise TomosSyntaxError(
                f"Environment variable {env_variable_name} is not defined", guess_line_nr_from=args
            )
        made_out_token = Token(expected_type, os.environ[env_variable_name], line=args[0].line)
        literal_parsers = {
            "int": self.INT,
            "real": self.REAL,
            "char": self.CHAR_LITERAL,
            "bool": self.bool_literal,
        }
        return literal_parsers[expected_type](made_out_token)

    def variable(self, args):
        if len(args) == 1 and isinstance(args[0], Variable):
            return args[0]
        return Variable(name_token=args[0])

    def VAR_NAME(self, token):
        return Variable(name_token=token)

    def v_accessed(self, args):
        if len(args) != 2:
            raise TomosSyntaxError(
                f"Invalid variable field access: {args}", guess_line_nr_from=args
            )
        var = args[0]
        field_name = args[1]
        var.traverse_append(Variable.ACCESSED_FIELD, field_name)
        return var

    def v_deref(self, args):
        var = args[0]
        var.traverse_append(Variable.DEREFERENCE)
        return var

    def v_arrow_access(self, args):
        if len(args) != 2:
            raise TomosSyntaxError(
                f"Invalid variable field arrow access: {args}", guess_line_nr_from=args
            )
        var = args[0]
        field_name = args[1]
        var.traverse_append(Variable.DEREFERENCE)
        var.traverse_append(Variable.ACCESSED_FIELD, field_name)
        return var

    def v_indexed(self, args):
        if len(args) == 1:
            raise TomosSyntaxError(f"Invalid variable indexing: {args}", guess_line_nr_from=args)
        var = args[0]
        indexing = args[1:]
        var.traverse_append(Variable.ARRAY_INDEXING, indexing)
        return var

    def expr(self, args):
        if len(args) != 1:
            raise TomosSyntaxError(f"Invalid expression: {args}", guess_line_nr_from=args)
        return args[0]

    # LITERALS
    def parse_literal(self, _class, token):
        literal = _class(token=token)
        if self.do_eval_literals:
            evaluator = ExpressionEvaluator()
            try:
                evaluator.eval(literal, state=None)
            except Exception:
                type_name = _class._type.__name__
                raise TomosSyntaxError(
                    f"Invalid literal for {type_name}: {token.value}", guess_line_nr_from=token
                )
        return literal

    def INT(self, token):
        return self.parse_literal(IntegerLiteral, token)

    def INF(self, token):
        return self.parse_literal(IntegerLiteral, token)

    def NULL(self, token):
        return NullLiteral(token)

    def REAL(self, token):
        return self.parse_literal(RealLiteral, token)

    def bool_literal(self, args):
        token = args[0]
        return self.parse_literal(BooleanLiteral, token)

    def CHAR_LITERAL(self, token):
        return self.parse_literal(CharLiteral, token)

    def ENUM_LITERAL(self, token):
        for tname, ttype in type_registry.list_types():
            if isinstance(ttype, Enum):
                if ttype.is_valid_value(token.value):
                    return EnumLiteral(token)

        raise TomosSyntaxError(f"Invalid enum literal: {token}", guess_line_nr_from=token)

    def array_of(self, args):
        if len(args) == 2:
            array_type = ArrayOf(of=args[1], axes=args[0])
            array_type.eval_axes_expressions(ExpressionEvaluator(), None)
            return array_type
        else:
            raise TomosSyntaxError(
                f"Invalid array type definition with args: {args}", guess_line_nr_from=args
            )

    def array_axes(self, args):
        return tuple(args)

    def array_axis(self, args):
        if len(args) == 1:
            return ArrayAxis(0, args[0])
        elif len(args) == 2:
            return ArrayAxis(args[0], args[1])
        else:
            raise TomosSyntaxError(f"Invalid array size. Axis {args}", guess_line_nr_from=args)

    def array_axis_from(self, args):
        if len(args) == 1:
            return args[0]
        else:
            raise TomosSyntaxError(f"Invalid array size. Axis from {args}", guess_line_nr_from=args)

    def array_axis_to(self, args):
        if len(args) == 1:
            return args[0]
        else:
            raise TomosSyntaxError(f"Invalid array size. Axis to {args}", guess_line_nr_from=args)
