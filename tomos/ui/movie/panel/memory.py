from manim import VGroup, Rectangle, Text, BOLD
from manim import LEFT, RIGHT, DOWN, UP

from tomos.ui.movie.panel.vars import Variable


class MemoryBlock(VGroup):

    def __init__(self, scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stack_blackboard = Rectangle(width=3, height=7, color="black", fill_color="white", fill_opacity=0.1)
        self.heap_blackboard = Rectangle(width=3, height=7, color="black", fill_color="YELLOW_D", fill_opacity=0.1)
        assert self.stack_blackboard.width == 3
        self.stack_blackboard.move_to((1.5, 0, 0))

        self.add(self.stack_blackboard)
        self.add(self.heap_blackboard)
        self.heap_blackboard.next_to(self.stack_blackboard, RIGHT)

        self.vars_by_name = {}
        self.last_block = None

    def process_snapshot(self, snapshot):
        print('PROCESSING SNAP')
        for thing in snapshot.diff.new_cells:
            print("Adding", thing)
            if isinstance(thing, str):
                cell = snapshot.state.cell_by_names[thing]
                self.add_var(thing, cell.var_type, cell.value)
        for thing in snapshot.diff.changed_cells:
            print("Changing", thing)
            if isinstance(thing, str):
                cell = snapshot.state.cell_by_names[thing]
                self.set_value(thing, cell.value)

    def add_var(self, name, _type, value):
        var = Variable(name, _type, value)
        var.align_to(self.stack_blackboard, LEFT)
        if self.last_block is None:
            var.align_to(self.stack_blackboard, UP)
        else:
            var.align_to(self.last_block, DOWN)
            var.shift(DOWN * var.rect.height * 2.5)
        self.stack_blackboard.add(var)
        self.last_block = var
        self.vars_by_name[name] = var

    def set_value(self, name, value, animator=None):
        var = self.vars_by_name[name]
        new_value = var.build_value_text(value)
        if animator is None:
            if hasattr(var, 'value'):
                var.remove(var.value)
            var.value = new_value
            var.add(var.value)
        else:
            animator(var, var.value, new_value)
            var.add(var.value)

