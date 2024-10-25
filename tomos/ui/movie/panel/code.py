from tomos.ui.movie.texts import build_text
from manim import (
    Code as ManimCode,
    UP, DOWN, LEFT, RIGHT,
    YELLOW,
    Text, SurroundingRectangle, VGroup)


class Highlighter(VGroup):

    def __init__(self, line, rect, line_number):
        super().__init__(line, rect)
        self.line_number = line_number

    def show_info(self, msg, color=None):
        hint = build_text(str(msg), font="Monospace")
        hint.set_color(YELLOW)
        # hint.scale(0.2)
        hint.next_to(self, RIGHT)
        return hint


class TomosCode(ManimCode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_code_txt = kwargs['code']
        self.line_blocks = self.code
        self.main_highlighter = self.build_highlighter()
        self.code.add(self.main_highlighter)

    def build_highlighter(self):
        max_columns = max([len(line) for line in self.source_code_txt.split('\n')])
        invisible_line = Text("-" * max_columns)
        invisible_line.set_opacity(0)
        rect = SurroundingRectangle(invisible_line, buff=0.2, corner_radius=0.2)
        rect.set_opacity(0.2)
        return Highlighter(invisible_line, rect, line_number=None)

    def highlight_line(self, line_number):
        prev_number = self.main_highlighter.line_number
        if prev_number == line_number:
            return
        reference = self.code[line_number - 1]
        if prev_number is None:
            self.main_highlighter.align_to(reference, LEFT)
            self.main_highlighter.shift(0.05 * LEFT)
            direction = DOWN
        elif prev_number < line_number:
            direction = DOWN
        else:
            direction = UP

        self.main_highlighter.align_to(reference, direction)
        self.main_highlighter.shift(0.025 * DOWN) # to make the line centered respect text
        self.main_highlighter.line_number = line_number

    def build_hint(self, msg):
        return self.main_highlighter.show_info(msg)
