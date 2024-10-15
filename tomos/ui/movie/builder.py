from manim import Scene, LEFT, RIGHT, FadeIn, FadeOut
from manim import constants, config
from manim.utils.file_ops import open_file as open_media_file

from tomos.ayed2.ast.program import VarDeclaration
from tomos.ayed2.ast.sentences import While, If, Assignment

from tomos.ui.movie.panel.code import TomosCode
from tomos.ui.movie.panel.memory import MemoryBlock


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
        memory_block = MemoryBlock(self)
        self.add(memory_block)
        memory_block.to_edge(RIGHT)
        for i, snapshot in enumerate(self.timeline.timeline):
            if isinstance(snapshot.last_sentence, VarDeclaration):
                memory_block.process_snapshot(snapshot)
                continue
            code_block.highlight_line(snapshot.line_number)
            self.wait(self.delay)

            if isinstance(snapshot.last_sentence, (If, While)):
                guard = snapshot.last_sentence.guard
                guard_value = snapshot.expression_values[guard]
                for action in code_block.show_info_in_line(guard_value):
                    self.play(action, delay=self.delay)

            if isinstance(snapshot.last_sentence, Assignment):
                expr = snapshot.last_sentence.expr
                expr_value = snapshot.expression_values[expr]
                for action in code_block.show_info_in_line(expr_value):
                    self.play(action, delay=self.delay)

            memory_block.process_snapshot(snapshot)

            import os
            if os.getenv("STOP") == str(i):
                print("STOP at", i)
                break

        self.wait()

    def fade_out(self, obj):
        self.play(FadeOut(obj), delay=self.delay)

    def fade_in(self, obj):
        self.play(FadeIn(obj), delay=self.delay)


def build_movie(source_code_path, timeline, delay=0.5):
    lq = constants.QUALITIES["low_quality"]
    config.frame_rate = lq["frame_rate"]
    config.pixel_height = lq["pixel_height"]
    config.pixel_width = lq["pixel_width"]
    scene = TomosScene(filename=source_code_path, timeline=timeline, delay=delay)
    print("Rendering video")
    print(len(scene.timeline.timeline))
    scene.render()

    open_media_file(scene.renderer.file_writer.movie_file_path)


if __name__ == '__main__':
    import sys
    build_movie(sys.argv[1], None)
