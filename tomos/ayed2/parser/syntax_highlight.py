from pygments import highlight as pyg_highlight
from pygments.formatters import TerminalTrueColorFormatter

from pygments_ayed2.lexer import Ayed2Lexer
from pygments_ayed2.style import Ayed2Style


def highlight(code):
    lexer = Ayed2Lexer()
    formatter = TerminalTrueColorFormatter(style=Ayed2Style)
    return pyg_highlight(code, lexer, formatter)
