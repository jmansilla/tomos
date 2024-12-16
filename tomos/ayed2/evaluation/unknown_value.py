class _UnknownSingleton:
    def __repr__(self):
        return "<?>"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, _UnknownSingleton):
            return True
        return False

    def __hash__(self) -> int:
        return str(self).__hash__()


# Singleton for unknown values.
UnknownValue = _UnknownSingleton()
