from logging import getLogger
from pathlib import Path

from tomos.ui.movie import configs
from tomos.ui.movie.scene import TomosScene

logger = getLogger(__name__)


def build_movie_from_file(source_code_path, timeline, delay=0.5):
    output_path = Path.cwd() / "output_tomos" / Path(source_code_path).name
    source_code = open(source_code_path, 'r').read()
    return build_movie(source_code, timeline, output_path)


def build_movie(code, timeline, output_path):
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    scene = TomosScene(code, timeline=timeline, output_path=output_path)
    logger.info(f"Rendering movie to {output_path}")
    return scene.render()


if __name__ == '__main__':
    import sys
    build_movie_from_file(sys.argv[1], None)
