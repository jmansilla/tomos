class BasicType:
    def __init__(self, token):
        self._token = token
    def __repr__(self) -> str:
        return self.__class__.__name__

class IntType(BasicType): pass
class BoolType(BasicType): pass
class PointerOf(BasicType):
    def __init__(self, token, of):
        super().__init__(token)
        self._of = of
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._of})'

type_map = {
    'int': IntType,
    'bool': BoolType,
}