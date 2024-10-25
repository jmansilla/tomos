from manim import Scene, LEFT, RIGHT, Transform, FadeIn, FadeOut
from manim import constants, config
from manim.utils.file_ops import open_file as open_media_file

from tomos.ayed2.ast.program import VarDeclaration
from tomos.ayed2.ast.sentences import While, If, Assignment

from tomos.ui.movie.panel.code import TomosCode
from tomos.ui.movie.panel.memory import MemoryBlock


class TomosBaseScene(Scene):
    def animate_value_change(self, var, old, new):
        prev_color = var.color
        # need rectangle-box resizing?
        new_width = var.rect.suggested_width(new)
        expand_width = max(0, (new_width - var.rect.width) / 2)

        rect_animations = var.rect.animate.set_color("PURE_GREEN")
        if expand_width > 0:
            new.shift(RIGHT * expand_width)
            rect_animations = rect_animations.stretch_to_fit_width(new_width).shift(RIGHT * expand_width)
        self.play(Transform(old, new),
                    rect_animations)
        self.play(var.rect.animate.set_color(prev_color))

    def animate_arrow_change(self, var, old_arrow, new_arrow):
        self.play(Transform(old_arrow, new_arrow))


class TomosScene(TomosBaseScene):

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
        memory_block = MemoryBlock(self)
        self.add(memory_block)
        memory_block.to_edge(RIGHT)
        for i, snapshot in enumerate(self.timeline.timeline):
            if isinstance(snapshot.last_sentence, VarDeclaration):
                memory_block.process_snapshot(snapshot)
                continue
            code_block.highlight_line(snapshot.line_number)

            if isinstance(snapshot.last_sentence, (If, While)):
                guard = snapshot.last_sentence.guard
                guard_value = snapshot.expression_values[guard]
                guard_hint = code_block.build_hint(guard_value)
                self.play(FadeIn(guard_hint), delay=self.delay)
                self.play(FadeOut(guard_hint), delay=self.delay)

            if isinstance(snapshot.last_sentence, Assignment):
                expr = snapshot.last_sentence.expr
                expr_value = snapshot.expression_values[expr]
                expr_hint = code_block.build_hint(expr_value)
                self.play(FadeIn(expr_hint), delay=self.delay)
                self.play(expr_hint.animate.shift(RIGHT * 4), delay=self.delay)
                self.play(FadeOut(expr_hint), delay=self.delay)

            memory_block.process_snapshot(snapshot)

            import os
            if os.getenv("STOP") == str(i):
                print("STOP at", i)
                break

        self.wait()



def build_movie(source_code_path, timeline, delay=0.5):
    quality = constants.QUALITIES["medium_quality"]
    config.frame_rate = quality["frame_rate"]
    config.pixel_height = quality["pixel_height"]
    config.pixel_width = quality["pixel_width"]
    scene = TomosScene(filename=source_code_path, timeline=timeline, delay=delay)
    print("Rendering video")
    print(len(scene.timeline.timeline))
    scene.render()

    open_media_file(scene.renderer.file_writer.movie_file_path)


if __name__ == '__main__':
    import sys
    build_movie(sys.argv[1], None)
