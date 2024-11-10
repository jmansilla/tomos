from skitso.atom import Container, Point
from skitso import movement
from skitso.shapes import Rectangle

from tomos.ayed2.ast.types import PointerOf
from tomos.ayed2.evaluation.state import MemoryAddress

from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text
from tomos.ui.movie.panel.vars import Variable, PointerVar


board_width, board_height = configs.MEMORY_BOARD_SIZE
padding = configs.PADDING


class Blackboard(Container):
    def __init__(self, x, y, fill_color):
        position = Point(x, y)
        super().__init__(position)
        self.rect = Rectangle(x, y, board_width, board_height, fill_color=fill_color,
                             stroke_color="gray", stroke_width=3)
        self.add(self.rect)
        self.last_block = []

    def add_var(self, var):
        var.to_edge(self, movement.LEFT_EDGE)
        var.shift(movement.RIGHT * padding)

        if not self.last_block:
            var.to_edge(self, movement.TOP_EDGE)
            var.shift(movement.DOWN * padding)
        else:
            var.to_edge(self.last_block[-1], movement.BOTTOM_EDGE)
            var.shift(movement.DOWN * (var.box_height + padding))
        self.last_block.append(var)
        self.add(var)


class MemoryBlock(Container):

    def __init__(self):
        super().__init__(Point(0, 0))  # placed at origin. Will be shifted later.

        title_size = configs.BASE_FONT_SIZE * 1.5
        stack_title = build_text("STACK", font_size=title_size, bold=True)
        self.add(stack_title)
        heap_title = build_text("HEAP", font_size=title_size, bold=True)
        heap_title.shift(movement.RIGHT * (board_width + padding))
        self.add(heap_title)

        boards_y = stack_title.box_height + padding
        self.stack_blackboard = Blackboard(0, boards_y, fill_color="#3B1C32")
        self.heap_blackboard = Blackboard(
            heap_title.position.x, boards_y, fill_color="#6A1E55"
        )

        self.add(self.heap_blackboard)
        self.add(self.stack_blackboard)

        self.vars_by_name = {}  # the index of the vars in the memory

    def process_snapshot(self, snapshot):
        print('PROCESSING SNAPSHOT')
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
        for name_or_addr in snapshot.diff.deleted_cells:
            print("Deleting", name_or_addr)
            in_heap = isinstance(name_or_addr, MemoryAddress)
            self.delete_var(name_or_addr, in_heap=in_heap)

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
        blackboard.add_var(var)
        # var.to_edge(blackboard, movement.LEFT_EDGE)
        # var.shift(movement.RIGHT * padding)

        # last_block = self.last_block.get(blackboard, None)
        # if last_block is None:
        #     var.to_edge(blackboard, movement.TOP_EDGE)
        #     var.shift(movement.DOWN * padding)
        # else:
        #     var.to_edge(last_block, movement.BOTTOM_EDGE)
        #     var.shift(movement.DOWN * (var.box_height + padding))
        # self.last_block[blackboard] = var
        self.vars_by_name[name] = var

        # self.add(var)

    def delete_var(self, name, in_heap):
        if not in_heap:
            raise NotImplementedError()
        var = self.vars_by_name[name]
        self.vars_by_name.pop(name)
        self.heap_blackboard.remove(var)

    def set_value(self, name, value):
        var = self.vars_by_name[name]
        var.set_value(value)

