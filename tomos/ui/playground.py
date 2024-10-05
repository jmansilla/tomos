"""

Usage: playground.py [options] <source>

Options:
    --run           Runs the program
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


if __name__ == "__main__":
    opts = docopt(__doc__)  # type: ignore

    source = opts["<source>"]
    ast = parser.parse(open(source).read())

    if opts["--showast"]:
        print(ASTPrettyFormatter().format(ast))

    if opts["--run"]:
        delay = opts["--delay"]
        try:
            delay = float(delay)
        except ValueError:
            print(f"Invalid delay: {delay}")
            exit(1)
        pre_hooks = [
            ShowSentence(source, full=True),
            Sleeper(delay)
        ]

        if opts["--step"]:
            pre_hooks.append(wait_for_input)

        interpreter = Interpreter(ast,
                                  pre_hooks=pre_hooks,
                                  post_hooks=[ShowState('state.mem'), ])
        final_state = interpreter.run()
        print(final_state)

