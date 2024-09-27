from typing import Any
import factory

from lark.lexer import Token
from tomos.ayed2.ast.expressions import (
    IntegerConstant,
    BooleanConstant,
    RealConstant,
    Variable,
)
from tomos.ayed2.ast.operators import UnaryOp, BinaryOp, UnaryOpTable, BinaryOpTable
from tomos.ayed2.evaluation.state import State


def get_tkn_faker_value(ob, faker_attr_name="token_faker_value"):
    # auxiliary method for params factories
    return getattr(ob.factory_parent, faker_attr_name)


class TokenFactory(factory.Factory):
    class Meta:
        model = Token

    type = factory.Faker("word")
    value = factory.Faker("word")


class StateFactory(factory.Factory):
    class Meta:
        model = State


class AbstractConstantFactory(factory.Factory):
    class Meta:
        abstract = True

    token = factory.SubFactory(
        TokenFactory,
        value=factory.LazyAttribute(
            lambda ob: str(ob.factory_parent.faker_value).lower()
        ),
    )


class IntegerConstantFactory(AbstractConstantFactory):
    class Meta:
        model = IntegerConstant

    class Params:
        faker_value = factory.Faker("pyint", min_value=0)


class RealConstantFactory(AbstractConstantFactory):
    class Meta:
        model = RealConstant

    class Params:
        faker_value = factory.Faker("pyfloat", min_value=0)


class BooleanConstantFactory(AbstractConstantFactory):
    class Meta:
        model = BooleanConstant

    class Params:
        faker_value = factory.Faker("pybool")


class VariableFactory(factory.Factory):
    class Meta:
        model = Variable

    name_token = factory.SubFactory(TokenFactory)

class UnaryOpFactory(factory.Factory):
    class Meta:
        model = UnaryOp

    class Params:
        token_faker_value = factory.Faker(
            "random_element", elements=UnaryOpTable.keys()
        )

    op_token = factory.SubFactory(
        TokenFactory, value=factory.LazyAttribute(get_tkn_faker_value)
    )

    expr = factory.SubFactory(IntegerConstantFactory)


class BinaryOpFactory(factory.Factory):
    class Meta:
        model = BinaryOp

    class Params:
        token_faker_value = factory.Faker(
            "random_element", elements=BinaryOpTable.keys()
        )

    op_token = factory.SubFactory(
        TokenFactory, value=factory.LazyAttribute(get_tkn_faker_value)
    )

    left_expr = factory.SubFactory(IntegerConstantFactory)
    right_expr = factory.SubFactory(IntegerConstantFactory)
