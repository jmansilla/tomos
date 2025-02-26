import factory

from tomos.ayed2.ast.types import type_registry
from tomos.ayed2.ast.program import VarDeclaration
from tomos.ayed2.ast.sentences import Assignment, If, While


class AssignmentFactory(factory.Factory):
    class Meta:
        model = Assignment

    dest_variable = factory.SubFactory("tests.ayed2.factories.expressions.VariableFactory")
    expr = factory.SubFactory("tests.ayed2.factories.expressions.IntegerLiteralFactory")


class VarDeclarationFactory(factory.Factory):
    class Meta:
        model = VarDeclaration

    class Params:
        faker_type = factory.Faker(
            "random_element", elements=type_registry.type_map.values()
        )

    variable = factory.SubFactory("tests.ayed2.factories.expressions.VariableFactory")
    var_type = factory.LazyAttribute(lambda ob: ob.faker_type())


class IfFactory(factory.Factory):
    class Meta:
        model = If

    guard = factory.SubFactory("tests.ayed2.factories.expressions.BooleanLiteralFactory")
    then_sentences = factory.List([
        factory.SubFactory(AssignmentFactory) for _ in range(3)
    ])
    else_sentences = factory.List([
        factory.SubFactory(AssignmentFactory) for _ in range(3)
    ])


class WhileFactory(factory.Factory):
    class Meta:
        model = While

    guard = factory.SubFactory("tests.ayed2.factories.expressions.BooleanLiteralFactory")
    sentences = factory.List([
        factory.SubFactory(AssignmentFactory) for _ in range(3)
    ])
