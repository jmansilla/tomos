from os import system
from tomos.ayed2.parser.syntax_highlight import highlight


def _clear_screen():
    system('cls' if system == 'nt' else 'clear')


class ShowSentence:
    # would be better better to use some package for code coloring
    # and for coloring in general
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, filename, full=False):
        self.filename = filename
        self.full = full
        source_hl = highlight(open(filename).read())
        self.source_lines = source_hl.split('\n')

    def __call__(self, last_sentence, state, sentence_to_run):
        if self.full:
            _clear_screen()
            for i, line in enumerate(self.source_lines, start=1):
                prefix = f"{i: 5}"
                if i == sentence_to_run.line_number:
                    prefix = self.OKGREEN + prefix + self.ENDC
                print(prefix, line)
            print("-" * 80)
            print("Abstract-Sentence to run:")
            print("\t", self.HEADER, sentence_to_run, self.ENDC)

        else:
            print(self.OKCYAN, sentence_to_run, self.ENDC)
            actual_line = self.source_lines[sentence_to_run.line_number - 1]
            print(self.OKBLUE, actual_line, self.ENDC)

