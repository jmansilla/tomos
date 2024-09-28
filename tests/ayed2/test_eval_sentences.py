from unittest import TestCase
from unittest.mock import patch

from tomos.ayed2.evaluation.interpreter import SentenceEvaluator

from .factories.state import StateFactory
from .factories.sentences import VarDeclarationFactory, AssignmentFactory, IfFactory


class BaseSentEval(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.evaluator = SentenceEvaluator()

    def run_eval(self, sentence, state=None):
        if state is None:
            state = StateFactory()
        return self.evaluator.eval(sentence, state)


class TestEvalVarDeclarationsAndAssignments(BaseSentEval):

    def test_eval_var_declaration(self):
        sentence = VarDeclarationFactory()
        state = StateFactory()
        with patch.object(state, "declare_static_variable") as mock_declare:
            self.run_eval(sentence, state)
            mock_declare.assert_called_once_with(sentence.name, sentence.var_type)

    def test_eval_assignment(self):
        sentence = AssignmentFactory()
        state = StateFactory()
        with patch.object(self.evaluator, "visit_expr") as mock_eval_expr:
            mock_eval_expr.return_value = some_value = 9
            with patch.object(state, "set_static_variable_value") as mock_set:
                self.run_eval(sentence, state)
                mock_set.assert_called_once_with(sentence.name, some_value, sentence.dereferenced)


class TestEvalIfThenElse(BaseSentEval):

    def test_eval_if_then_else(self):
        s_if = IfFactory()
        state = StateFactory()
        with patch.object(self.evaluator, "visit_expr") as mock_eval_expr:
            mock_eval_expr.return_value = True  # shall use then branch
            with patch.object(self.evaluator, "visit_list") as mock_eval_list:
                self.run_eval(s_if, state)
                mock_eval_list.assert_called_once_with(s_if.then_sentences, state=state, children=[])
            mock_eval_expr.return_value = False  # shall use then branch
            with patch.object(self.evaluator, "visit_list") as mock_eval_list:
                self.run_eval(s_if, state)
                mock_eval_list.assert_called_once_with(s_if.else_sentences, state=state, children=[])
