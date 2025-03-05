import itertools
import re


class MetadataParser:
    def __init__(self, source_code):
        self.source_code = source_code

    def detect_metadata(self, name, pattern, handler):
        with open(self.source_code) as f:
            for line_nr, line in enumerate(f, 1):  # line numbers on a file starts at 1
                if pattern.match(line):
                    handler(name, line_nr, line)


class DetectExplicitCheckpoints:
    # pattern will express lines that ends with " // checkpoint" or "checkpoint:", and
    # some optionally followed by the checkpoint name
    pattern = re.compile(r".*//\s*checkpoint(\W|$)(:.*)?")

    def __init__(self, ast, source_code):
        self.ast = ast
        self.source_code = source_code
        self.metadata_parser = MetadataParser(source_code)
        sentences = list(SentencesLister().list_sentences(self.ast))
        numbered_sentences = [(s.line_number, s) for s in sentences]
        self.numbered_sentences = dict(numbered_sentences)

    def detect(self):
        self.errors = []
        self.metadata_parser.detect_metadata("checkpoint", self.pattern, self.handler)
        if self.errors:
            print(f"ERROR: {len(self.errors)} errors detected. Fix them and try again.")
            exit(1)

    def handler(self, name, line_nr, line):
        sent = self.numbered_sentences.get(line_nr, None)
        if sent:
            sent.set_parsing_metadata(name, True)
            print(f"Found {name} for line {line_nr}, on sentence {sent}")
        else:
            print(f"ERROR: Couldn't find sentence for line {line_nr}")
            self.errors.append((line_nr, line))


class SentencesLister:

    def children_if(self, node):
        return itertools.chain(node.then_sentences, node.else_sentences)

    def children_for(self, node):
        return iter(node.sentences)

    def children_while(self, node):
        return iter(node.sentences)

    def children_body(self, node):
        return itertools.chain(node.var_declarations, node.sentences)

    def visit(self, node, *args, **kwargs):
        node_type_name = type(node).__name__.lower()
        visit_method_name = f"visit_{node_type_name}"

        children_method = getattr(self, f"children_{node_type_name}", None)
        if children_method:
            children = [self.visit(c, *args, **kwargs) for c in children_method(node)]
        else:
            children = []
        kwargs["children"] = children

        method = getattr(self, visit_method_name, self.generic_visit)
        return method(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        children_results = kwargs["children"]
        return itertools.chain([node], itertools.chain(*children_results))

    def visit_body(self, node, *args, **kwargs):
        children_results = kwargs["children"]
        return itertools.chain(*children_results)

    def list_sentences(self, ast):
        return self.visit(ast.body)
