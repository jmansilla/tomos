"""
Tomos, the Ayed2 interpreter.
    Interprets the program, and prints the final state.

Usage:
  tomos [options] <source> [--cfg=<conf>]...
  tomos -h | --help
  tomos --version

Options:
    --movie=<fname>       Generates a movie with the execution (implicitly cancels --no-run if set).
                          Must be a .mp4 file.
    --autoplay            Autoplay the movie. Implicitly sets --movie=movie.mp4 if not set.
    --no-run              Skips executing the program. Useful for debugging.
    --no-final-state      Skips printing the final state.
    --showast             Show the abstract syntax tree.
    --save-state=<fname>  Save the final state to a file.
    --load-state=<fname>  Load the state from a file.
    --cfg=<conf>          Overrides configurations one by one.
    --version             Show version and exit.
    -h --help             Show this message and exit.
"""
import importlib.metadata
from pathlib import Path
from sys import exit

from docopt import docopt

from tomos.ayed2.parser import parser
from tomos.ayed2.evaluation.interpreter import Interpreter
from tomos.ui.interpreter_hooks import ASTPrettyFormatter
from tomos.ui.interpreter_hooks import RememberState


def main():
    opts = docopt(__doc__)  # type: ignore
    if opts["--version"]:
        version = importlib.metadata.version("tomos")
        print(f"Tomos version {version}")
        exit(0)

    source_path = opts["<source>"]
    opts["--run"] = not opts["--no-run"]

    ast = parser.parse(open(source_path).read())

    if opts["--showast"]:
        print(ASTPrettyFormatter().format(ast))

    if opts["--autoplay"] and not opts["--movie"]:
        opts["--movie"] = "movie.mp4"
    if opts["--movie"] and not opts["--run"]:
        opts["--run"] = True

    if opts["--run"]:
        pre_hooks = []
        post_hooks = []

        load_state_from = opts["--load-state"]

        if opts["--movie"]:
            if not opts["--movie"].endswith(".mp4"):
                print("Movie must be a .mp4 file.")
                exit(1)
            timeline = RememberState()
            post_hooks = [timeline]

        interpreter = Interpreter(ast,
                                  pre_hooks=pre_hooks,
                                  post_hooks=post_hooks)
        final_state = interpreter.run(load_state_from=load_state_from)

        if opts["--movie"]:
            # slow import. Only needed if --movie is set
            from tomos.ui.movie.builder import build_movie_from_file
            movie_path = Path(opts["--movie"])
            build_movie_from_file(source_path, movie_path, timeline)
            if opts["--autoplay"]:
                if not movie_path.exists():
                    print(f"Unable to find movie {movie_path}")
                    exit(1)
                play_movie(movie_path)

        if opts["--save-state"]:
            final_state.save_to_file(opts["--save-state"])

        if not opts["--no-final-state"]:
            # Hard to follow. Double negation means DO SHOW IT.
            print(final_state)


def play_movie(movie_path):
    from unittest import mock
    from moviepy import VideoFileClip
    from tomos.ui.patch_moviepy import FixedPreviewer
    with mock.patch("moviepy.video.io.ffplay_previewer.FFPLAY_VideoPreviewer", new=FixedPreviewer):
        clip = VideoFileClip(movie_path)
        clip.preview()
        clip.close()


if __name__ == "__main__":
    main()