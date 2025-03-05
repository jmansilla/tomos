from time import sleep
from tomos.ayed2.ast.program import VarDeclaration


def wait_for_input(last_sentence, state, sentence_to_run):
    # would be better to react to any key press
    if isinstance(sentence_to_run, VarDeclaration):
        return
    input("[Press Enter]... ")


class Sleeper:
    def __init__(self, delta) -> None:
        self.delta = delta

    def __call__(self, last_sentence, state, sentence_to_run):
        if not isinstance(sentence_to_run, VarDeclaration):
            sleep(self.delta)
