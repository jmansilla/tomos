class ASTNode:

    @property
    def line_number(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
