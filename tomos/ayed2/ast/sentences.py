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
    def __repr__(self) -> str:
        return "Skip()"


class ProcedureCall(Sentence):
    # TODO
    pass


class BuiltinCall(ProcedureCall):
    def __init__(self, name, args):
        self._name = name
        self._args = args

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
    def __init__(self, name, expr, pointed=False):
        self._name_token = name
        self._expr = expr
        self.pointed = pointed

    @property
    def name(self):
        return self._name_token.value

    @property
    def expr(self):
        return self._expr

    def __repr__(self) -> str:
        star = "*" if self.pointed else ""
        return f"Assignment(dest={star}{self.name}, expr={self.expr})"
