from tomos.visit import NodeVisitor
from tomos.ayed2.ast.expressions import Expr
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator
from tomos.ayed2.evaluation.state import State


class Interpreter:
    """
    Interpreter for sentences.
    """
    def __init__(self, ast, pre_hooks=None, post_hooks=None):
        self.ast = ast
        self.state = State()
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    def _run_pre_hooks(self, next_sentence):
        if not self.pre_hooks:
            return
        for hook in self.pre_hooks:
            hook(self.previous_sentence, self.state, next_sentence)

    def _run_post_hooks(self):
        if not self.post_hooks:
            return
        for hook in self.post_hooks:
            hook(self.previous_sentence, self.state)

    def _run_sentence(self, kind, sentence_to_run):
        if not hasattr(self, 'previous_sentence'):
            self.previous_sentence = None

        self._run_pre_hooks(sentence_to_run)
        if kind == 'body':
            self.state = self.main_interpreter.eval(sentence_to_run, state=self.state)
        else:
            print('running', kind)
        self.previous_sentence = sentence_to_run
        self._run_post_hooks()

    def run(self):
        self.main_interpreter = _Interpreter()
        for name, section in [
            ('typedef', self.ast.typedef_section),
            ('funprocdef', self.ast.funprocdef_section),
            ('body', self.ast.body)
        ]:
            for sentence in section:
                self._run_sentence(name, sentence)

        return self.state


class _Interpreter(NodeVisitor):
    """
    Interpreter for sentences.
    """
    def eval(self, sentence, state):
        return self.visit(sentence, state=state)

    def get_visit_name_from_type(self, _type):
        # Transforms CammelCase to snake_case, and preppends "visit_"
        if issubclass(_type, Expr):
            _type = Expr
        result = super().get_visit_name_from_type(_type)
        return result

    def visit_expr(self, expr, **kw):
        state = kw["state"]
        return ExpressionEvaluator().eval(expr, state)

    def visit_skip(self, sentence, **kw):
        state = kw["state"]
        return state

    def visit_var_declaration(self, sentence, **kw):
        state = kw["state"]
        state.declare_static_variable(sentence.name, sentence.var_type)
        return state

    def visit_assignment(self, sentence, **kw):
        state = kw["state"]
        value = self.visit_expr(sentence.expr, state=state)
        state.set_static_variable_value(sentence.name, value, sentence._contained_at)
        return state

    def visit_builtin_call(self, sentence, **kw):
        state = kw["state"]
        if sentence._name == 'alloc':
            variable = sentence._args[0]
            state.alloc(variable.name)
        elif sentence._name == 'free':
            variable = sentence._args[0]
            state.free(variable.name)
        return state
