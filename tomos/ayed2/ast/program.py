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


class Program(ProgramExpression):
    def __init__(self, typedef_section, funprocdef_section, body):
        self.typedef_section = typedef_section
        self.funprocdef_section = funprocdef_section
        self.body = body

    def __repr__(self) -> str:
        return f"Program({self.body})"

    def pretty(self):
        result = f"Program\n"
        indent = "  "
        for section_name in ["typedef_section", "funprocdef_section", "body"]:
            section = getattr(self, section_name)
            result += f"{indent}{section_name}\n"
            entries = f"\n".join(map(lambda c: indent * 2 + repr(c), section))
            result += entries
        return result


class Body(ProgramExpression):
    def __init__(self, var_declarations, sentences):
        self.var_declarations = var_declarations
        self.sentences = sentences

    def __iter__(self):
        yield from self.var_declarations
        yield from self.sentences


class VarDeclaration(ProgramExpression):
    def __init__(self, name, declared_type):
        self._name_token = name
        self._type = declared_type

    @property
    def name(self):
        return self._name_token.value

    @property
    def line_number(self):
        return self._name_token.line

    @property
    def var_type(self):
        return self._type

    def __repr__(self) -> str:
        return f"VarDeclaration(name={self.name}, type={self.var_type})"


class TypeDeclaration(ProgramExpression):
    # TODO
    pass


class FunctionDeclaration(ProgramExpression):
    # TODO
    pass


class ProcedureDeclaration(ProgramExpression):
    # TODO
    pass
