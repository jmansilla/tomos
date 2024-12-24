import re


class VisitError(Exception):
    pass


class NodeVisitor:

    def get_visit_name_from_type(self, _type):
        # Transforms CammelCase to snake_case, and preppends "visit_"
        name = _type.__name__
        pattern = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
        return "visit_" + pattern.sub("_", name).lower()

    def visit(self, node, *args, **kwargs):
        if hasattr(node, "children"):
            children = [self.visit(c, *args, **kwargs) for c in node.children()]
        else:
            children = []
        kwargs["children"] = children

        custom_visit_method = self.get_visit_name_from_type(type(node))
        method = getattr(self, custom_visit_method, self.generic_visit)
        return method(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        raise VisitError(f"No behaviour defined for {node} ({type(node)})")
