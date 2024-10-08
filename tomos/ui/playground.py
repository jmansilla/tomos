"""

Usage: playground.py [options] <source>

Options:
    --run           Runs the program
    --movie         Generates a movie with the execution.
                    Must be used with --run, and ignores --step and --delay
    --step          Steps the program [default: False]
    --delay <n>     Delay in seconds [default: 0.5]
    --showast       Show the abstract syntax tree
    --help          Show this message and exit
"""
from sys import exit
from docopt import docopt

from tomos.ayed2.parser import parser
from tomos.ayed2.evaluation.interpreter import Interpreter
from tomos.ui.interpreter_hooks import ShowSentence, ShowState, Sleeper, wait_for_input
from tomos.ui.interpreter_hooks.show_ast import ASTPrettyFormatter


from dataclasses import dataclass
class RememberState:
    @dataclass
    class Frame:
        line_number: int
        state: object

    def __init__(self):
        self.timeline = []

    def __call__(self, last_sentence, state):
        f = self.Frame(last_sentence.line_number, state)
        self.timeline.append(f)


if __name__ == "__main__":
    opts = docopt(__doc__)  # type: ignore

    source_path = opts["<source>"]
    ast = parser.parse(open(source_path).read())

    if opts["--showast"]:
        print(ASTPrettyFormatter().format(ast))

    if opts["--movie"] and not opts["--run"]:
        opts["--run"] = True

    if opts["--run"]:
        if opts["--movie"]:
            timeline = RememberState()
            pre_hooks = []
            post_hooks = [timeline]
        else:
            delay = opts["--delay"]
            try:
                delay = float(delay)
            except ValueError:
                print(f"Invalid delay: {delay}")
                exit(1)
            pre_hooks = [
                ShowSentence(source_path, full=True),
                Sleeper(delay)
            ]

            if opts["--step"]:
                pre_hooks.append(wait_for_input)

            post_hooks = [ShowState('state.mem'), ]

        interpreter = Interpreter(ast,
                                  pre_hooks=pre_hooks,
                                  post_hooks=post_hooks)
        final_state = interpreter.run()
        if opts["--movie"]:
            print("Generating movie...")
            from tomos.ui.movie.builder import build_video
            build_video(source_path, timeline)

        print(final_state)

