from collections import namedtuple
import pickle

from tomos.ayed2.ast.types import type_registry


Execution = namedtuple("Execution", ["state", "type_registry"])


class Persist:

    @staticmethod
    def persist(execution_state, path):
        to_dump = Execution(execution_state, type_registry)
        with open(path, "wb") as f:
            pickle.dump(to_dump, f)

    @staticmethod
    def load_from_file(path):
        with open(path, "rb") as f:
            exec = pickle.load(f)
        type_registry.merge(exec.type_registry)
        return exec.state
