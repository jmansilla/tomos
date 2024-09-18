from unittest import TestCase

from tomos.ayed2.ast.expressions import *


class TestEval(TestCase):
    def test_eval(self):
        source = "var x: int"
