from copy import deepcopy
from dataclasses import dataclass


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
        # what is still in a_stack, needs to be deleted cells
        diff.deleted_cells = list(a_stack.keys())

        for addr, val in b_heap.items():
            if addr not in a_heap:
                diff.new_cells.append(addr)
            else:
                if val != a_heap[addr]:
                    diff.changed_cells.append(addr)
                a_heap.pop(addr)
        # what is still in a_heap, needs to be deleted cells
        diff.deleted_cells += list(a_heap.keys())

        return diff


@dataclass
class Frame:
    line_number: int
    last_sentence: object
    state: object
    expression_values: dict
    diff: StateDiff


class RememberState:

    def __init__(self):
        self.timeline = []

    def __call__(self, last_sentence, state, expression_values):
        if not self.timeline:
            diff = StateDiff.create_diff(type(state)(), state)
        else:
            diff = StateDiff.create_diff(self.timeline[-1].state, state)
        f = Frame(last_sentence.line_number, last_sentence,
                  deepcopy(state),
                  expression_values, diff)
        self.timeline.append(f)

