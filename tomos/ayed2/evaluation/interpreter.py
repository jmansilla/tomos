import logging

from tomos.visit import NodeVisitor
from tomos.ayed2.ast.expressions import Expr
from tomos.ayed2.ast.types import ArrayOf
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator
from tomos.ayed2.evaluation.state import State

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Interpreter:
    """
    Interpreter for sentences.
    Exposes the public interface of interpreter.
    """
    def __init__(self, ast, pre_hooks=None, post_hooks=None):
        self.ast = ast
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    def run(self):
        self.sent_evaluator = SentenceEvaluator()
        self.last_executed_sentece = None  # For hooks
        state = State()
        for name, section in [
            ('typedef', self.ast.typedef_section),
            ('funprocdef', self.ast.funprocdef_section),
            ('body', self.ast.body)
        ]:
            logger.info('Running section %s', name)
            state = self.run_sequence_of_sentences(section, state)

        return state

    def run_sequence_of_sentences(self, sentences, state):
        self.buffer_of_sentences = list(sentences)
        while self.buffer_of_sentences:
            # Caution. This buffer can be modified in the middle of the loop
            sentence = self.buffer_of_sentences.pop(0)
            state, extra_sentences = self._run_sentence(sentence, state)
            if extra_sentences:
                self.buffer_of_sentences = extra_sentences + self.buffer_of_sentences

        return state

    def _run_sentence(self, sentence_to_run, state):
        self._run_pre_hooks(sentence_to_run, state)

        new_state, injected_block = self.sent_evaluator.eval(sentence_to_run, state=state)

        self.last_executed_sentece = sentence_to_run
        self._run_post_hooks(state)
        return new_state, injected_block

    def _run_pre_hooks(self, next_sentence, state):
        for hook in self.pre_hooks:
            hook(self.last_executed_sentece, state, next_sentence)

    def _run_post_hooks(self, state):
        for hook in self.post_hooks:
            hook(self.last_executed_sentece, state)


class SentenceEvaluator(NodeVisitor):
    """
    Evaluates sentences
    """
    def __init__(self) -> None:
        super().__init__()
        self.expression_evaluator = ExpressionEvaluator()

    def eval(self, sentence, state):
        # Evaluate the sentence in a given state.
        # Returns (new_state, extra_sentences)
        result = self.visit(sentence, state=state)
        if isinstance(result, State):
            return result, []
        elif isinstance(result, tuple) and len(result) == 2:
            return result
        else:
            raise ValueError(f"Unexpected result {result}")

    def get_visit_name_from_type(self, _type):
        # Transforms CammelCase to snake_case, and preppends "visit_"
        if issubclass(_type, Expr):
            _type = Expr
        result = super().get_visit_name_from_type(_type)
        return result

    def visit_if(self, sentence, **kw):
        state = kw["state"]
        if self.visit_expr(sentence.guard, state=state):
            injected_block = sentence.then_sentences
        else:
            injected_block = sentence.else_sentences
        return state, injected_block

    def visit_while(self, sentence, **kw):
        state = kw["state"]
        if self.visit_expr(sentence.guard, state=state):
            injected_block = list(sentence.sentences) + [sentence]
        else:
            injected_block = []
        return state, injected_block

    def visit_expr(self, expr, **kw):
        state = kw["state"]
        return self.expression_evaluator.eval(expr, state)

    def visit_skip(self, sentence, **kw):
        state = kw["state"]
        return state

    def visit_var_declaration(self, sentence, **kw):
        state = kw["state"]
        if isinstance(sentence.var_type, ArrayOf):
            sentence.var_type.eval_axes_expressions(self.expression_evaluator, state)
        state.declare_static_variable(sentence.name, sentence.var_type)
        return state

    def visit_assignment(self, assignment, **kw):
        state = kw["state"]
        value = self.visit_expr(assignment.expr, state=state)
        modifiers = assignment.modifiers
        if modifiers.array_indexing:
            for i, index_expr in enumerate(modifiers.array_indexing):
                assert isinstance(index_expr, Expr)
                index_value = self.visit_expr(index_expr, state=state)
                modifiers.array_indexing[i] = index_value
        state.set_variable_value(assignment.name, value, modifiers)
        return state

    def visit_builtin_call(self, sentence, **kw):
        state = kw["state"]
        if sentence.name == 'alloc':
            variable = sentence.args[0]
            state.alloc(variable.name)
        elif sentence.name == 'free':
            variable = sentence.args[0]
            state.free(variable.name)
        return state
