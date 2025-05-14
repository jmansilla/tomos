"""
Tomos, the Ayed2 interpreter.
    Interprets the program, and prints the final state.

Usage:
  tomos [options] <source> [--cfg=<conf>]...
  tomos -h | --help
  tomos --version

Options:
    --movie=<fname>       Generates a movie with the execution (implicitly
                          cancels --no-run if set). Must be a .mp4 file.
    --autoplay            Autoplay the movie. Implicitly sets --movie=movie.mp4
                          if not set.
    --explicit-frames     Only build frames for sentences that are explicitly
                          requested (ending in //checkpoint).
    --no-run              Skips executing the program. Useful for debugging.
    --no-final-state      Skips printing the final state.
    --showast             Show the abstract syntax tree.
    --save-state=<fname>  Save the final state to a file.
    --load-state=<fname>  Load the state from a file.
    --cfg=<conf>          Overrides configurations one by one.
    --version             Show version and exit.
    --verbose=<V>         Verbose mode. [default: 0]
    -h --help             Show this message and exit.
"""

import importlib.metadata
from pathlib import Path
from sys import exit, argv

from docopt import docopt

from tomos.ayed2.parser import parser
from tomos.ayed2.parser.metadata import DetectExplicitCheckpoints
from tomos.ayed2.evaluation.interpreter import Interpreter
from tomos.ayed2.evaluation.persistency import Persist
from tomos.exceptions import TomosSyntaxError
from tomos.ui.interpreter_hooks import ASTPrettyFormatter
from tomos.ui.interpreter_hooks import RememberState

GRAMMAR_LINK = "https://github.com/jmansilla/tomos/blob/main/tomos/ayed2/parser/grammar.lark"
EXAMPLES_LINK = "https://github.com/jmansilla/tomos/tree/main/demo/ayed2_examples"


def cli_parse(source_path, verbose_level):
    try:
        ast = parser.parse(open(source_path).read())
    except Exception as error:
        print("Parsing error:", type(error), error)
        if verbose_level == 1:
            print(f"For clarifying doubts, the grammar can be found at {GRAMMAR_LINK}")
            print(f"You can also check some examples at {EXAMPLES_LINK}")
        elif verbose_level >= 2:
            import traceback
            traceback.print_exc()
        exit(1)

    return ast


def main():
    my_argv = argv[1:]
    if "--verbose" in my_argv:
        level = my_argv.count("--verbose")
        for _ in range(level):
            my_argv.remove("--verbose")
        my_argv.append(f"--verbose={level}")

    opts = docopt(__doc__, argv=my_argv)

    verbose_level = int(opts["--verbose"])
    if opts["--version"]:
        version = importlib.metadata.version("tomos")
        print(f"Tomos version {version}")
        exit(0)

    source_path = opts["<source>"]
    opts["--run"] = not opts["--no-run"]

    # if loading a state, we may need to load some type-definitions
    # before parsing the program. It's suboptimal, but it works.
    if opts["--load-state"]:
        initial_state = Persist.load_from_file(opts["--load-state"])
    else:
        initial_state = None
    ast = cli_parse(source_path, verbose_level)

    if opts["--explicit-frames"]:
        DetectExplicitCheckpoints(ast, source_path).detect()

    if opts["--showast"]:
        print(ASTPrettyFormatter().format(ast))

    if opts["--autoplay"] and not opts["--movie"]:
        opts["--movie"] = "movie.mp4"
    if opts["--movie"] and not opts["--run"]:
        opts["--run"] = True

    if opts["--run"]:
        pre_hooks = []
        post_hooks = []

        if opts["--movie"]:
            if not opts["--movie"].endswith(".mp4"):
                print("Movie must be a .mp4 file.")
                exit(1)
            timeline = RememberState()
            post_hooks = [timeline]

        interpreter = Interpreter(ast, pre_hooks=pre_hooks, post_hooks=post_hooks)
        final_state = interpreter.run(initial_state=initial_state)

        if opts["--movie"]:
            # slow import. Only needed if --movie is set
            from tomos.ui.movie.builder import build_movie_from_file

            movie_path = Path(opts["--movie"])
            build_movie_from_file(
                source_path, movie_path, timeline, explicit_frames_only=opts["--explicit-frames"]
            )
            if opts["--autoplay"]:
                if not movie_path.exists():
                    print(f"Unable to find movie {movie_path}")
                    exit(1)
                play_movie(movie_path)

        if opts["--save-state"]:
            Persist.persist(final_state, opts["--save-state"])

        if not opts["--no-final-state"]:
            # Hard to read this if-guard. Double negation means DO SHOW IT.
            print("Final state:")
            print(' Stack:')
            MemoryPrinter.print_block(final_state.stack)
            print(' Heap:')
            MemoryPrinter.print_block(final_state.heap)


class MemoryPrinter:
    _idnt = "    "
    @classmethod
    def indent(cls, nesting):
        return cls._idnt * (nesting + 1)

    @classmethod
    def print_block(cls, contents, nesting=0):
        from tomos.ayed2.evaluation.memory import MetaMemCell
        indentation = cls.indent(nesting)
        for name, cell_or_val in contents.items():

            if isinstance(cell_or_val, MetaMemCell):
                val = cell_or_val.value  # type: ignore
                mini_title = f"{indentation}\"{name}\" ({cell_or_val.var_type}):"  # type: ignore
            else:
                val = cell_or_val
                mini_title = f"{indentation}\"{name}\":"
            if isinstance(val, (dict, list)):
                print(mini_title)
                cls.print_value(val, nesting)
            else:
                print(f"{mini_title} {val}")

    @classmethod
    def print_value(cls, val, nesting, suffix=""):
        if isinstance(val, dict):
            cls.print_block(val, nesting + 1)
        elif isinstance(val, list):
            inner_indent = cls.indent(nesting + 1)
            print(f"{inner_indent}[")
            for v in val:
                cls.print_value(v, nesting + 1, suffix=",")
            print(f"{inner_indent}]{suffix}")
        else:
            print(f"{cls.indent(nesting)}{val}{suffix}")


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
