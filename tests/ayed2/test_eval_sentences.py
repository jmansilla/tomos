from unittest import TestCase
from unittest.mock import patch

from tomos.ayed2.evaluation.interpreter import SentenceEvaluator

from .factories.state import StateFactory
from .factories.sentences import VarDeclarationFactory, AssignmentFactory, IfFactory, WhileFactory


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
            mock_eval_expr.return_value = True  # shall use "then" branch
            new_state, extra_sentences = self.run_eval(s_if, state)
            self.assertEqual(new_state, state)
            self.assertEqual(extra_sentences, s_if.then_sentences)
            mock_eval_expr.return_value = False  # shall use "else" branch
            new_state, extra_sentences = self.run_eval(s_if, state)
            self.assertEqual(new_state, state)
            self.assertEqual(extra_sentences, s_if.else_sentences)


class TestEvalWhile(BaseSentEval):

    def test_eval_if_then_else(self):
        s_while = WhileFactory()
        state = StateFactory()
        with patch.object(self.evaluator, "visit_expr") as mock_eval_expr:
            mock_eval_expr.return_value = False  # shall exit in the loop
            new_state, extra_sentences = self.run_eval(s_while, state)
            self.assertEqual(new_state, state)
            self.assertEqual(extra_sentences, [])

            mock_eval_expr.return_value = True  # shall remain in the loop
            new_state, extra_sentences = self.run_eval(s_while, state)
            self.assertEqual(new_state, state)
            self.assertEqual(extra_sentences, s_while.sentences + [s_while])

