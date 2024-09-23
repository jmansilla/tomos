from tomos.visit import NodeVisitor
from tomos.ayed2.ast.expressions import Expr
from tomos.ayed2.evaluation.expressions import ExpressionEvaluator
from tomos.ayed2.evaluation.state import State


class Interpreter:
    """
    Interpreter for sentences.
    """
    def __init__(self, ast, hooks=None):
        self.ast = ast
        self.state = State()
        self.hooks = hooks or []

    def _run_hooks(self, next_sentence):
        if not self.hooks:
            return
        if not hasattr(self, 'last_sentence'):
            self.last_sentence = None
        for hook in self.hooks:
            hook(self.last_sentence, self.state, next_sentence)
        self.last_sentence = next_sentence

    def run(self):
        self.main_interpreter = _Interpreter()
        self.last_sentence = None
        for sentence in self.ast.typedef_section:
            self._run_hooks(sentence)
            print ('running typedef', sentence)
        for sentence in self.ast.funprocdef_section:
            self._run_hooks(sentence)
            print ('running funprocdef', sentence)
        for sentence in self.ast.body:
            self._run_hooks(sentence)
            print ('running body', sentence)
            self.state = self.main_interpreter.eval(sentence, state=self.state)
        self._run_hooks(sentence)

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
        state.set_static_variable_value(sentence.name, value)
        return state

    def visit_if(self, sentence, **kw):
        pass