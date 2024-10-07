from manim import *

class CodeFromString(Scene):
    def construct(self):
        code = open('../../ayed2_examples/array_medium.ayed2', 'r').read()
        rendered_code = Code(code=code, tab_width=4, background="window",
                            language="ayed2", font="Monospace")
        self.add(rendered_code)
