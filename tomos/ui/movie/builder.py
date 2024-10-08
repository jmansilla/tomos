from manim import *
from manim.utils.file_ops import open_file as open_media_file


class CodeFromString(Scene):

    def __init__(self, *args, **kwargs):
        if 'filename' not in kwargs:
            raise ValueError("Please provide a filename")
        if 'timeline' not in kwargs:
            raise ValueError("Please provide a timeline")
        self.filename = kwargs.pop('filename')
        self.timeline = kwargs.pop('timeline')
        super().__init__(*args, **kwargs)

    def construct(self):
        source_code = open(self.filename, 'r').read()
        code = Code(code=source_code, tab_width=4, background="window",
                    language="ayed2", font="Monospace")
        self.add(code)
        code.scale(0.5)
        code.to_edge(LEFT)
        self.wait()


def build_movie(source_code_path, timeline):
    scene = CodeFromString(filename=source_code_path, timeline=timeline)
    print("Rendering video")
    print(len(scene.timeline.timeline))
    scene.render()

    open_media_file(scene.renderer.file_writer.movie_file_path)


if __name__ == '__main__':
    import sys
    build_movie(sys.argv[1], None)
