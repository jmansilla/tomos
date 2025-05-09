import logging

from tomos.ayed2.ast.expressions import Expr
from tomos.ayed2.ast.types import ArrayOf, IntType
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator
from tomos.ayed2.evaluation.limits import LIMITER
from tomos.ayed2.evaluation.state import State
from tomos.exceptions import TomosRuntimeError
from tomos.visit import NodeVisitor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Interpreter:
    """
    Interpreter for sentences/commands (generally speaking: instructions).
    Exposes the public interface of interpreter.
    """

    def __init__(self, ast, pre_hooks=None, post_hooks=None):
        self.ast = ast
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    def run(self, initial_state=None):
        # Type Definitions are processed at parsing time. No need to run them here now.
        # Section for funcprocdefs are not implemented yet. No need to run them here now.

        # So far, we just need to run the body.
        self.execution_counter = 0
        self.sent_evaluator = SentenceEvaluator()
        self.last_executed_sentence = None  # For hooks
        if initial_state:
            state = initial_state
            self._run_post_hooks(state)
        else:
            state = State()
        state.set_expressions_evaluator(self.sent_evaluator.expression_evaluator)
        next_sent = self.get_entry_point()
        while next_sent is not None:
            state, next_sent = self._run_sentence(next_sent, state)
            self.execution_counter += 1
            LIMITER.check_execution_counter_limits(self)
        return state

    def get_entry_point(self):
        # just the first instruction of the body. Can be changed in the future
        return next(iter(self.ast.body))

    def _run_sentence(self, sentence_to_run, state):
        self._run_pre_hooks(sentence_to_run, state)

        new_state, next_sent = self.sent_evaluator.eval(sentence_to_run, state=state)

        self.last_executed_sentence = sentence_to_run
        self._run_post_hooks(new_state)
        return new_state, next_sent

    def _run_pre_hooks(self, next_sentence, state):
        for hook in self.pre_hooks:
            hook(self.last_executed_sentence, state, next_sentence)

    def _run_post_hooks(self, state):
        # Hooks need to handle the case of last_executed_sentence == None
        # which happens when loading a state from file.
        expr_cache = self.sent_evaluator.flush_intermediate_evaluated_expressions()
        for hook in self.post_hooks:
            hook(self.last_executed_sentence, state, expr_cache)


class SentenceEvaluator(NodeVisitor):
    """
    Evaluates sentences
    """

    def __init__(self) -> None:
        super().__init__()
        self.expression_evaluator = ExpressionEvaluator()
        self.intermediate_evaluated_expressions = {}
        # This intermediate-evaluated-expressions is a cache usefull for UI and hooks in general
        # to know what's the value of some evaluated expressions during executing.
        # Example: how was the guard of an if evaluated

    def flush_intermediate_evaluated_expressions(self):
        result = self.intermediate_evaluated_expressions
        self.intermediate_evaluated_expressions = {}
        return result

    def eval(self, sentence, state):
        # Evaluate the sentence in a given state.
        # Returns (new_state, next_sentence)
        return self.visit(sentence, state=state)

    def get_visit_name_from_type(self, _type):
        # Transforms CammelCase to snake_case, and preppends "visit_"
        if issubclass(_type, Expr):
            _type = Expr
        result = super().get_visit_name_from_type(_type)
        return result

    def visit_if(self, if_sent, state, **kw):
        if self.visit_expr(if_sent.guard, state=state):
            sequence = if_sent.then_sentences
        else:
            sequence = if_sent.else_sentences

        if sequence:  # first sentence of corresponding branch
            next_sent = sequence[0]
        else:  # the branch is empty
            next_sent = if_sent.next_instruction

        return state, next_sent

    def visit_while(self, sentence, state, **kw):
        if self.visit_expr(sentence.guard, state=state):
            next_sent = sentence.sentences[0]
        else:
            next_sent = sentence.next_instruction
        return state, next_sent

    def visit_for(self, for_sent, state, **kw):
        var = for_sent.loop_variable
        if not for_sent.loop_in_progress: # Starting for loop.
            if var.name in state.list_declared_variables():
                raise RuntimeError(f"Variable {var.name} is already declared.")
            state.declare_static_variable(var.name, IntType(), read_only=True)
            for_sent.remove_loop_variable = True
            next_value = self.visit_expr(for_sent.start, state=state)
        else:
            next_value = for_sent.next_value(state.get_variable_value(var))
        end_value = self.visit_expr(for_sent.end, state=state)
        if for_sent.has_iterations_left(next_value, end_value):
            state.set_variable_value(var, next_value, permit_write_on_read_only=True)
            for_sent.loop_in_progress = True
            next_sent = for_sent.sentences[0]
        else:
            for_sent.loop_in_progress = False
            if for_sent.remove_loop_variable:
                state.undeclare_static_variable(var.name)
            next_sent = for_sent.next_instruction
        return state, next_sent

    def visit_expr(self, expr, state, **kw):
        value = self.expression_evaluator.eval(expr, state)
        self.intermediate_evaluated_expressions[expr] = value
        return value

    def visit_skip(self, sentence, state, **kw):
        return state, sentence.next_instruction

    def visit_var_declaration(self, sentence, state, **kw):
        if isinstance(sentence.var_type, ArrayOf):
            sentence.var_type.eval_axes_expressions(self.expression_evaluator, state)
        state.declare_static_variable(sentence.name, sentence.var_type)
        return state, sentence.next_instruction

    def visit_assignment(self, assignment, state, **kw):
        variable = assignment.dest_variable
        value = self.visit_expr(assignment.expr, state=state)
        state.set_variable_value(variable, value)
        return state, assignment.next_instruction

    def visit_builtin_call(self, sentence, state, **kw):
        name = sentence.name
        if name in ["alloc", "free"]:
            variable = sentence.args[0]
            method = getattr(state, name)
            method(variable)
        else:
            raise TomosRuntimeError(f"Unknown builtin call {sentence.name}")
        return state, sentence.next_instruction
