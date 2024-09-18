from unittest import TestCase

from tomos.ayed2.parser import parser


class TestParsing(TestCase):
    def test_parsing(self):
        source = "var x: int"
        ast = parser.parse(source)
        # this is not a test, just setting up the boilerplate
