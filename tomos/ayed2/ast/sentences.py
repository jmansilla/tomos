#  Sentences
#  =========
#      ⟨sentence⟩ ::= skip | ⟨assignment⟩ | ⟨procedurecall⟩ | ⟨if⟩ | ⟨while⟩ | ⟨for⟩
#      ⟨assignment⟩ ::= ⟨variable⟩ := ⟨expression⟩
#      ⟨while⟩ ::= while ⟨expression⟩ do ⟨sentences⟩
#      ⟨sentences⟩ ::= ⟨sentence⟩ ... ⟨sentence⟩
# [-]  ⟨procedurecall⟩ ::= ⟨id⟩ ( ⟨expression⟩ ... ⟨expression⟩ )
# [-]                    | alloc ( ⟨variable⟩ )
# [-]                    | free  ( ⟨variable⟩ )

#      ⟨if⟩ ::= if ⟨expression⟩ then ⟨sentences⟩ else ⟨sentences⟩
#      ⟨for⟩ ::= for ⟨id⟩ := ⟨expression⟩ to ⟨expression⟩ do ⟨sentences⟩
#              | for ⟨id⟩ := ⟨expression⟩ downto ⟨expression⟩ do ⟨sentences⟩


class Sentence:
    pass


class Skip(Sentence):
    def __init__(self, token):
        self._token = token

    @property
    def line_number(self):
        return self._token.line

    def __repr__(self) -> str:
        return "Skip()"


class ProcedureCall(Sentence):
    # TODO
    pass


class BuiltinCall(ProcedureCall):
    def __init__(self, name, args):
        self._name = name
        self._args = args

    @property
    def line_number(self):
        return self._name.line

    def __repr__(self) -> str:
        return f"BuiltinCall(name={self._name}, args={self._args})"


class If(Sentence):
    def __init__(self, guard, then_body, else_body):
        self._guard = guard
        self._then_body = then_body
        self._else_body = else_body


class While(Sentence):
    def __init__(self, guard, body):
        self._guard = guard
        self._body = body


class For(Sentence):
    def __init__(self, name, start, end, body):
        self._name_token = name
        self._start = start
        self._end = end
        self._body = body


class Assignment(Sentence):
    def __init__(self, dest, expr):
        self._dest_variable = dest
        self._expr = expr

    @property
    def name(self):
        return self._dest_variable.name

    @property
    def line_number(self):
        return self._dest_variable.line_number

    @property
    def _dereferenced(self):
        return self._dest_variable._dereferenced

    @property
    def expr(self):
        return self._expr

    def __repr__(self) -> str:
        full_name = self._dest_variable.symbols_name
        return f"Assignment(dest={full_name}, expr={self.expr})"
