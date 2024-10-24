from manim import VGroup, Write, Rectangle, BOLD
from manim import LEFT, RIGHT, DOWN, UP

from tomos.ayed2.ast.types import PointerOf
from tomos.ayed2.evaluation.state import MemoryAddress

from tomos.ui.movie.texts import build_text
from tomos.ui.movie.panel.vars import Variable, PointerVar


class MemoryBlock(VGroup):

    def __init__(self, scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = scene
        self.stack_blackboard = Rectangle(width=3, height=7, color="black",
                                          fill_color="white", fill_opacity=0.1)
        self.heap_blackboard = Rectangle(width=3, height=7, color="black",
                                         fill_color="YELLOW_D", fill_opacity=0.1)
        assert self.stack_blackboard.width == 3
        self.stack_blackboard.move_to((1.5, 0, 0))

        self.add(self.stack_blackboard)
        self.add(self.heap_blackboard)
        self.heap_blackboard.next_to(self.stack_blackboard, RIGHT)
        stack_title = build_text("STACK", weight=BOLD)
        heap_title = build_text("HEAP", weight=BOLD)
        self.add(stack_title, heap_title)
        stack_title.next_to(self.stack_blackboard, UP * .5)
        heap_title.next_to(self.heap_blackboard, UP * .5)

        self.vars_by_name = {}  # the index of the vars in the memory
        self.last_block = {}

    def process_snapshot(self, snapshot):
        print('PROCESSING SNAP')
        for name_or_addr in snapshot.diff.new_cells:
            print("Adding", name_or_addr)
            if isinstance(name_or_addr, MemoryAddress):
                cell = snapshot.state.heap[name_or_addr]
                self.add_var(name_or_addr, cell.var_type, cell.value, in_heap=True)
            else:
                cell = snapshot.state.cell_by_names[name_or_addr]
                self.add_var(name_or_addr, cell.var_type, cell.value)
        for name_or_addr in snapshot.diff.changed_cells:
            print("Changing", name_or_addr)
            if isinstance(name_or_addr, MemoryAddress):
                cell = snapshot.state.heap[name_or_addr]
            else:
                cell = snapshot.state.cell_by_names[name_or_addr]
            self.set_value(name_or_addr, cell.value)

    def add_var(self, name, _type, value, in_heap=False):
        # Create the correct var sprite
        if isinstance(_type, PointerOf):
            vars_index = self.vars_by_name
            var = PointerVar(vars_index, name, _type, value, in_heap=in_heap)
        else:
            var = Variable(name, _type, value, in_heap=in_heap)

        # Select the correct blackboard and add&align the var
        if in_heap:
            blackboard = self.heap_blackboard
        else:
            blackboard = self.stack_blackboard
        var.align_to(blackboard, LEFT)

        last_block = self.last_block.get(id(blackboard), None)
        if last_block is None:
            var.align_to(blackboard, UP)
        else:
            var.align_to(last_block, DOWN)
            var.shift(DOWN * var.rect.height * 2)
        self.last_block[id(blackboard)] = var
        self.vars_by_name[name] = var

        if in_heap:
            self.scene.play(Write(var))
        blackboard.add(var)

    def set_value(self, name, value):
        var = self.vars_by_name[name]
        var.set_value(value, transition_animator=self.scene)

