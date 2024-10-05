from pygments import highlight as pyg_highlight
from pygments.formatters import TerminalFormatter, TerminalTrueColorFormatter, Terminal256Formatter

from pygments.lexer import RegexLexer
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Punctuation, Other


class Ayed2Lexer(RegexLexer):
    name = 'Ayed2'
    tokens = {
        'root': [
            (r'\s+', Text),  # whitespace
            (r'//.*?$', Comment),  # single line comment
            (r'var', Keyword),  # keyword
            (r'int|char|bool|real|array|pointer|of', Keyword.Type),  # types
            (r':=', Punctuation.Assignment),  # classes
            (r'if|then|else|fi|while|do|od', Keyword),  # control flow keywords
            (r'alloc|free', Name.Builtin),  # built-in functions
            (r'==|!=|<|<=|>|>=', Operator),  # comparison operators
            (r'\+\+|--|\+|-|\*|/|%', Operator),  # arithmetic operators
            (r'\&\&|\|\|', Operator),  # logical operators
            (r'null|true|false|inf', Name.Builtin),  # literals
            (r'"\w+"', String),  # string literals
            (r'\d+\.\d+', Number.Float),  # floating point
            (r'\d+', Number.Integer),  # integers
            (r'\w+', Name),  # identifiers
            (r'\(', Punctuation),  # parentheses
            (r'\)', Punctuation),  # parentheses
            (r'\[', Punctuation),  # brackets
            (r'\]', Punctuation),  # brackets
            (r'\{', Punctuation),  # braces
            (r'\}', Punctuation),  # braces
            (r';', Punctuation),  # statement terminator
        ],
    }


from pygments.style import Style
from pygments.token import Token

class MyStyle(Style):
        styles = {
            Token.Keyword.Type:     'ansibrightblue',
            Token.String:           'ansibrightblue',
            Token.Number:           'ansibrightcyan',
            Token.Operator:         'ansibrightred',
            Token.Keyword:          'ansibrightgreen',
            Token.Name:             'ansiwhite',
            Token.Punctuation:      'ansicyan',
            Punctuation.Assignment: 'ansibrightyellow',
        }


def highlight(code):
    lexer = Ayed2Lexer()
    formatter = TerminalTrueColorFormatter(style=MyStyle)
    return pyg_highlight(code, lexer, formatter)

