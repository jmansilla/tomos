from lark import Transformer, Token
from lark.exceptions import UnexpectedInput

from tomos.ayed2.ast.types import *
from tomos.ayed2.ast.expressions import *
from tomos.ayed2.ast.sentences import *
from tomos.ayed2.ast.operators import *
from tomos.ayed2.ast.program import *
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator


class TreeToAST(Transformer):
    do_eval_literals = True

    def program(self, args):
        tdef, fdef, body = args
        return Program(typedef_section=tdef.children, funprocdef_section=fdef.children, body=body)

    sentences = list

    def body(self, args):
        vardef, sentences = args
        return Body(var_declarations=vardef.children, sentences=sentences)

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

    def SKIP(self, token):
        return Skip(token)

    def var_declaration(self, args):
        var, var_type = args
        return VarDeclaration(variable=var, var_type=var_type)

    def pointer(self, args):
        assert len(args) == 1
        token = args[0]
        pointed_type = self.type(args)
        return PointerOf(of=pointed_type)

    def type(self, args):
        assert len(args) == 1
        token = args[0]
        if token.value not in type_map:
            raise UnexpectedInput(f"Unknown type: {token.value}")
        return type_map[token.value]()

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
            raise UnexpectedInput(f"Invalid binary expression: {args}")

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

    def variable(self, args):
        if len(args) == 1 and isinstance(args[0], Variable):
            return args[0]
        return Variable(name_token=args[0])

    def variable_dereferenced(self, args):
        var = args[0]
        var.dereferenced = True
        return var

    def expr(self, args):
        if len(args) != 1:
            raise UnexpectedInput(f"Invalid expression: {args}")
        return args[0]

    # LITERALS
    def parse_literal(self, _class, token):
        literal = _class(token=token)
        if self.do_eval_literals and not isinstance(literal, NullLiteral):
            evaluator = ExpressionEvaluator()
            try:
                evaluator.eval(literal, state=None)
            except Exception as e:
                type_name = _class._type.__name__
                raise UnexpectedInput(f"Invalid literal for {type_name}: {token.value}")
        return literal

    def INT(self, token):
        return self.parse_literal(IntegerLiteral, token)

    def INF(self, token):
        return self.parse_literal(IntegerLiteral, token)

    def NULL(self, token):
        return self.parse_literal(NullLiteral, token)

    def REAL(self, token):
        return self.parse_literal(RealLiteral, token)

    def bool_literal(self, args):
        token = args[0]
        return self.parse_literal(BooleanLiteral, token)

    def CHAR_LITERAL(self, token):
        return self.parse_literal(CharLiteral, token)

    # array definition parsing
    def array_of(self, args):
        if len(args) == 2:
            return ArrayOf(of=args[1], axes=args[0])

    def array_axes(self, args):
        return tuple(args)

    def array_axis(self, args):
        if len(args) == 1:
            return ArrayAxis(0, args[0])
        elif len(args) == 2:
            return ArrayAxis(args[0], args[1])
        else:
            raise UnexpectedInput(f"Invalid array size. Axis {args}")

    def array_axis_from(self, args):
        if len(args) == 1:
            return args[0]
        else:
            raise UnexpectedInput(f"Invalid array size. Axis from {args}")

    def array_axis_to(self, args):
        if len(args) == 1:
            return args[0]
        else:
            raise UnexpectedInput(f"Invalid array size. Axis to {args}")

