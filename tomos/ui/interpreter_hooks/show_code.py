from os import system
from tomos.ayed2.parser.syntax_highlight import highlight
from tomos.ui.colors import bcolors


def _clear_screen():
    system("cls" if system == "nt" else "clear")


class ShowSentence:

    def __init__(self, filename, full=False):
        self.filename = filename
        self.full = full
        source_hl = highlight(open(filename).read())
        self.source_lines = source_hl.split("\n")

    def __call__(self, last_sentence, state, sentence_to_run):
        if self.full:
            _clear_screen()
            for i, line in enumerate(self.source_lines, start=1):
                prefix = f"{i: 3}"
                if i == sentence_to_run.line_number:
                    prefix = bcolors.OKGREEN + "->" + prefix + bcolors.ENDC
                else:
                    prefix = "  " + prefix
                print(prefix, line)
            print("-" * 80)
            print("Abstract-Sentence to run:")
            print("\t", bcolors.HEADER, sentence_to_run, bcolors.ENDC)

        else:
            print(bcolors.OKCYAN, sentence_to_run, bcolors.ENDC)
            actual_line = self.source_lines[sentence_to_run.line_number - 1]
            print(bcolors.OKBLUE, actual_line, bcolors.ENDC)
