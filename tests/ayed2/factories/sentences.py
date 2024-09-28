import factory

from tomos.ayed2.ast.types import type_map
from tomos.ayed2.ast.program import VarDeclaration
from tomos.ayed2.ast.sentences import Assignment, If


class AssignmentFactory(factory.Factory):
    class Meta:
        model = Assignment

    dest_variable = factory.SubFactory("tests.ayed2.factories.expressions.VariableFactory")
    expr = factory.SubFactory("tests.ayed2.factories.expressions.IntegerConstantFactory")


class VarDeclarationFactory(factory.Factory):
    class Meta:
        model = VarDeclaration

    class Params:
        faker_type = factory.Faker(
            "random_element", elements=type_map.values()
        )

    variable = factory.SubFactory("tests.ayed2.factories.expressions.VariableFactory")
    var_type = factory.LazyAttribute(lambda ob: ob.faker_type)


class IfFactory(factory.Factory):
    class Meta:
        model = If

    guard = factory.SubFactory("tests.ayed2.factories.expressions.BooleanConstantFactory")
    then_sentences = factory.List([
        factory.SubFactory(AssignmentFactory) for _ in range(3)
    ])
    else_sentences = factory.List([
        factory.SubFactory(AssignmentFactory) for _ in range(3)
    ])
