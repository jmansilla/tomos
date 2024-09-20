from typing import Any
import factory

from lark.lexer import Token
from tomos.ayed2.ast.expressions import (
    IntegerConstant, BooleanConstant, RealConstant, Variable
)
from tomos.ayed2.evaluation.state import State


class TokenFactory(factory.Factory):
    class Meta:
        model = Token

    type = factory.Faker("word")
    value = factory.Faker("word")


class StateFactory(factory.Factory):
    class Meta:
        model = State


class IntegerConstantFactory(factory.Factory):
    class Meta:
        model = IntegerConstant

    token = factory.SubFactory(TokenFactory)


class RealConstantFactory(factory.Factory):
    class Meta:
        model = RealConstant

    token = factory.SubFactory(TokenFactory)


class BooleanConstantFactory(factory.Factory):
    class Meta:
        model = BooleanConstant

    token = factory.SubFactory(TokenFactory)


class VariableFactory(factory.Factory):
    class Meta:
        model = Variable

    name = factory.SubFactory(TokenFactory)