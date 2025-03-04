from copy import deepcopy
from dataclasses import dataclass

from tomos.ayed2.ast.program import TypeDeclaration, VarDeclaration


@dataclass
class StateDiff:
    new_cells: list
    changed_cells: list
    deleted_cells: list

    @staticmethod
    def create_diff(state_a, state_b):
        # the user of this has at hand the state_b, and wants to know
        # what has changed from state_a -> state_b
        # So, in "new_cells" will be the cells that are in b but not in a
        diff = StateDiff([], [], [])
        a_stack = {name: cell.value for name, cell in state_a.stack.items()}
        a_heap = {addr: cell.value for addr, cell in state_a.heap.items()}
        b_stack = {name: cell.value for name, cell in state_b.stack.items()}
        b_heap = {addr: cell.value for addr, cell in state_b.heap.items()}

        for name, val in b_stack.items():
            if name not in a_stack:
                diff.new_cells.append(name)
            else:
                if val != a_stack[name]:
                    diff.changed_cells.append(name)
                a_stack.pop(name)
        # what is still in a_stack, needs to be deleted cells
        diff.deleted_cells = list(a_stack.keys())

        for addr, val in b_heap.items():
            if addr not in a_heap:
                diff.new_cells.append(addr)
            else:
                if val != a_heap[addr]:
                    diff.changed_cells.append(addr)
                a_heap.pop(addr)
        # what is still in a_heap, needs to be deleted cells
        diff.deleted_cells += list(a_heap.keys())

        return diff


class LoadedFromFile:
    line_number = 0


@dataclass
class Frame:
    line_number: int
    just_executed: object
    state: object
    expression_values: dict
    diff: StateDiff
    next: object | None

    def get_cell(self, name_or_addr):
        from tomos.ayed2.evaluation.state import MemoryAddress

        if isinstance(name_or_addr, MemoryAddress):
            return self.state.heap[name_or_addr]  # type: ignore
        else:
            return self.state.stack[name_or_addr]  # type: ignore

    @property
    def explicit_checkpoint(self):
        if not hasattr(self.just_executed, "get_parsing_metadata"):
            return False
        return self.just_executed.get_parsing_metadata("checkpoint")  # type: ignore


class RememberState:
    STATE_LOADED_FROM_FILE = LoadedFromFile()

    def __init__(self):
        self.timeline = []

    def __call__(self, last_sentence, state, expression_values):
        if not self.timeline:
            # only in the case that the first call is with last_sentence==None
            # we will asume that the state was loaded from a file
            if last_sentence is None:
                last_sentence = self.STATE_LOADED_FROM_FILE
            diff = StateDiff.create_diff(type(state)(), state)
        else:
            diff = StateDiff.create_diff(self.timeline[-1].state, state)
        f = Frame(
            last_sentence.line_number, last_sentence, deepcopy(state), expression_values, diff, None
        )
        if self.timeline:
            self.timeline[-1].next = f
        self.timeline.append(f)

    def loaded_initial_snapshot(self):
        if self.timeline and self.timeline[0].just_executed == self.STATE_LOADED_FROM_FILE:
            return self.timeline[0]
        else:
            return None

    def list_declaration_snapshots(self):
        return [
            frame
            for frame in self.timeline
            if isinstance(frame.just_executed, (TypeDeclaration, VarDeclaration))
        ]

    def list_sentence_snapshots(self):
        return [
            frame
            for frame in self.timeline
            if not isinstance(
                frame.just_executed, (TypeDeclaration, VarDeclaration, LoadedFromFile)
            )
        ]
