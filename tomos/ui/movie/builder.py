from manim import Code as ManimCode, Scene, UP, DOWN, LEFT, RIGHT, YELLOW, FadeIn, FadeOut, Text, SurroundingRectangle, VGroup
from manim.utils.file_ops import open_file as open_media_file

from tomos.ayed2.ast.program import VarDeclaration
from tomos.ayed2.ast.sentences import While, If, Assignment


class Highlighter(VGroup):

    def __init__(self, line, rect, line_number):
        super().__init__(line, rect)
        self.line_number = line_number

    def show_info(self, msg, color=None):
        print('Calling show_info with ', msg)
        _msg = f"{msg} ({type(msg)})"
        hint = Text(_msg, font="Monospace")
        hint.set_color(YELLOW)
        hint.scale(0.3)
        hint.next_to(self, RIGHT)
        return [FadeIn(hint), FadeOut(hint)]


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

    def show_info_in_line(self, msg):
        return self.main_highlighter.show_info(msg)


class TomosScene(Scene):

    def __init__(self, filename, timeline, delay, *args, **kwargs):
        self.filename = filename
        self.timeline = timeline
        self.delay = delay
        super().__init__(*args, **kwargs)

    def construct(self):
        source_code = open(self.filename, 'r').read()
        code_block = TomosCode(
            code=source_code, tab_width=4, background="window",
            language="ayed2", font="Monospace"
        )

        self.add(code_block)
        code_block.scale(0.5)
        code_block.to_edge(LEFT)
        for i, snapshot in enumerate(self.timeline.timeline):
            if isinstance(snapshot.last_sentence, VarDeclaration):
                continue
            code_block.highlight_line(snapshot.line_number)
            self.wait(self.delay)
            if isinstance(snapshot.last_sentence, (If, While)):
                guard = snapshot.last_sentence.guard
                guard_value = snapshot.expression_values[guard]
                for action in code_block.show_info_in_line(guard_value):
                    self.play(action)
            if isinstance(snapshot.last_sentence, Assignment):
                expr = snapshot.last_sentence.expr
                expr_value = snapshot.expression_values[expr]
                for action in code_block.show_info_in_line(expr_value):
                    self.play(action)
                # self.wait(self.delay)
            if i == 10:
                break

        self.wait()


def build_movie(source_code_path, timeline, delay=0.5):
    scene = TomosScene(filename=source_code_path, timeline=timeline, delay=delay)
    print("Rendering video")
    print(len(scene.timeline.timeline))
    scene.render()

    open_media_file(scene.renderer.file_writer.movie_file_path)


if __name__ == '__main__':
    import sys
    build_movie(sys.argv[1], None)
