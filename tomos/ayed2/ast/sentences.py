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
        self.token = token

    @property
    def line_number(self):
        return self.token.line

    def __repr__(self) -> str:
        return "Skip()"


class ProcedureCall(Sentence):
    # TODO
    pass


class BuiltinCall(Sentence):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @property
    def line_number(self):
        return self.name.line

    def __repr__(self) -> str:
        return f"BuiltinCall(name={self.name}, args={self.args})"


class If(Sentence):
    def __init__(self, guard, then_body, else_body):
        self.guard = guard
        self.then_body = then_body
        self.else_body = else_body


class While(Sentence):
    def __init__(self, guard, body):
        self.guard = guard
        self.body = body


class For(Sentence):
    def __init__(self, name, start, end, body):
        self.name_token = name
        self.start = start
        self.end = end
        self.body = body


class Assignment(Sentence):
    def __init__(self, dest, expr):
        self.dest_variable = dest
        self.expr = expr

    @property
    def name(self):
        return self.dest_variable.name

    @property
    def line_number(self):
        return self.dest_variable.line_number

    @property
    def dereferenced(self):
        return self.dest_variable.dereferenced

    def __repr__(self) -> str:
        full_name = self.dest_variable.symbols_name
        return f"Assignment(dest={full_name}, expr={self.expr})"
