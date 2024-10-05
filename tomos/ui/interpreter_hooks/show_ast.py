from tomos.visit import NodeVisitor

class ASTPrettyFormatter(NodeVisitor):
    indent = "    "

    def format(self, ast):
        return self.visit(ast)

    def generic_visit(self, node, *args, **kwargs):
        return repr(node)

    def stuff_with_children(self, title, children):
        result = f"{title}"
        if children:
            entries = f"\n".join(
                map(self.visit, children)
            )
            entries = "\n" + entries
            entries = entries.replace("\n", "\n" + self.indent)
            result += entries
        else:
            result += "\n"
        return result

    def stuff_with_sections(self, title, sections):
        result = f"{title}\n"

        for section_name, section in sections.items():
            sec_result = f"\n{self.indent}{section_name}"
            if section:  # may be an empty list
                entries = f"\n".join(
                    map(self.visit, section)
                )
                entries = "\n" + entries
                entries = entries.replace("\n", "\n" + self.indent * 2)
                sec_result += entries
            else:
                sec_result = sec_result + "\n"

            result += sec_result
        double_nl = "\n\n"
        while double_nl in result:
            result = result.replace(double_nl, "\n")
        return result

    def visit_program(self, node, *args, **kwargs):
        sections = {
            n: getattr(node, n) for n in ["typedef_section", "funprocdef_section", "body"]
        }
        return self.stuff_with_sections("Program", sections)

    def visit_while(self, node, *args, **kwargs):
        return self.stuff_with_children(str(node), node.sentences)

    def visit_if(self, node, *args, **kwargs):
        sections = {
            "then": node.then_sentences,
            "else": node.else_sentences,
        }
        return self.stuff_with_sections(str(node), sections)