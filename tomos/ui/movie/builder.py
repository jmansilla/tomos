from pathlib import Path

from tomos.ui.movie import configs
from tomos.ui.movie.scene import TomosScene


def build_movie(source_code_path, timeline, delay=0.5):

    output_path = Path.cwd() / "output_tomos" / Path(source_code_path).name
    output_path.mkdir(parents=True, exist_ok=True)
    scene = TomosScene(filename=source_code_path, timeline=timeline, output_path=output_path)
    print("Rendering video")
    print(len(scene.timeline.timeline))
    # scene.render()
    # open_media_file(scene.renderer.file_writer.movie_file_path)


if __name__ == '__main__':
    import sys
    build_movie(sys.argv[1], None)
