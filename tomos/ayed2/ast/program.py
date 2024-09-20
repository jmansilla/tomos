#  Program
#  =======
# [-]  ⟨program⟩ ::= ⟨import_module⟩ ... ⟨import_module⟩ ⟨module⟩
#      ⟨module⟩ ::= ⟨typedecl⟩ ... ⟨typedecl⟩ ⟨funprocdecl⟩ ... ⟨funprocdecl⟩ ⟨body⟩
# [-]  ⟨funprocdecl⟩ ::= ⟨function⟩ | ⟨procedure⟩
#
#      ⟨body⟩ ::= ⟨variabledecl⟩ ... ⟨variabledecl⟩ ⟨sentences⟩
#      ⟨variabledecl⟩ ::= var ⟨id⟩ ... ⟨id⟩ : ⟨type⟩
#
# [-]  ⟨function⟩ ::= fun ⟨id⟩ ( ⟨funargument⟩ ... ⟨funargument⟩ ) ret ⟨funreturn⟩
# [-]                 where ⟨constraints⟩
# [-]                 in ⟨body⟩
# [-]  ⟨funargument⟩ ::= ⟨id⟩ : ⟨type⟩
# [-]  ⟨funreturn⟩ ::= ⟨id⟩ : ⟨type⟩
#
# [-]  ⟨procedure⟩ ::= proc ⟨id⟩ ( ⟨procargument⟩ ... ⟨procargument⟩ )
# [-]                  where ⟨constraints⟩
# [-]                  in ⟨body⟩
# [-]  ⟨procargument⟩ ::= ⟨io⟩ ⟨id⟩ : ⟨type⟩
#
# [-]  ⟨constraints⟩ ::= ⟨constraint⟩ ... ⟨constraint⟩
# [-]  ⟨constraint⟩ ::= ⟨typevariable⟩ : ⟨class⟩ ... ⟨class⟩


class ProgramExpression:
    pass


class Module(ProgramExpression):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self) -> str:
        return f"Module({self.children})"

    def pretty(self):
        title = f"module {self.name}\n\t"
        body = "\n\t".join(map(lambda c: repr(c), self.body))
        return title + body


class VarDeclaration(ProgramExpression):
    def __init__(self, name, declared_type):
        self._name_token = name
        self._type = declared_type

    @property
    def name(self):
        return self._name_token.value

    @property
    def type(self):
        return self._type

    def __repr__(self) -> str:
        return f"VarDeclaration(name={self.name}, type={self.type})"


class TypeDeclaration(ProgramExpression):
    # TODO
    pass


class FunctionDeclaration(ProgramExpression):
    # TODO
    pass


class ProcedureDeclaration(ProgramExpression):
    # TODO
    pass
