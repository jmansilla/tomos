from logging import getLogger

from skitso.atom import Container, Point
from skitso import movement
from skitso.shapes import Rectangle

from tomos.ayed2.evaluation.state import MemoryAddress

from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text
from tomos.ui.movie.panel.vars import create_variable_sprite


logger = getLogger(__name__)


board_width, board_height = configs.MEMORY_BOARD_SIZE
padding = configs.PADDING


class Blackboard(Container):
    def __init__(self, name, x, y, fill_color, adjust_width=1.0):
        self.name = name
        position = Point(x, y)
        super().__init__(position)
        self.rect = Rectangle(x, y, board_width * adjust_width, board_height,
                             fill_color=fill_color, stroke_color="gray", stroke_width=3)
        self.add(self.rect)
        self.last_block = []

    def add_var(self, var):
        var.to_edge(self, movement.LEFT_EDGE)
        if self.name == 'heap':
            var.shift(movement.RIGHT * padding * 3)
        else:
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

    def __init__(self, uses_heap, pointers_heap_to_heap):
        super().__init__(Point(0, 0))  # placed at origin. Will be shifted later.

        self.uses_heap = uses_heap
        self.pointers_heap_to_heap = pointers_heap_to_heap
        if not self.uses_heap:
            stack_adj = 2; heap_adj = 0
        elif self.pointers_heap_to_heap:
            stack_adj = .7; heap_adj = 1.3
        else:
            stack_adj = 1; heap_adj = 1

        title_size = configs.BASE_FONT_SIZE * 1.5
        stack_title = build_text("STACK", font_size=title_size, bold=True)
        self.add(stack_title)
        if self.uses_heap:
            heap_title = build_text("HEAP", font_size=title_size, bold=True)
            heap_title.shift(movement.RIGHT * (board_width * stack_adj + padding))
            self.add(heap_title)

        boards_y = stack_title.box_height + padding
        self.stack_blackboard = Blackboard('stack', 0, boards_y, fill_color="#3B1C32", adjust_width=stack_adj)
        if self.uses_heap:
            self.heap_blackboard = Blackboard(
                'heap', heap_title.position.x, boards_y, fill_color="#6A1E55",
                adjust_width=heap_adj
            )
            self.add(self.heap_blackboard)

        self.add(self.stack_blackboard)

        self.vars_by_name = {}  # the index of the vars in the memory

    def process_snapshot(self, snapshot):
        logger.debug('PROCESSING SNAPSHOT')
        for name_or_addr in snapshot.diff.new_cells:
            logger.debug("Adding", name_or_addr)
            cell = snapshot.get_cell(name_or_addr)
            in_heap = isinstance(name_or_addr, MemoryAddress)
            self.add_var(name_or_addr, cell.var_type, cell.value, in_heap=in_heap)
        for name_or_addr in snapshot.diff.changed_cells:
            logger.debug("Changing", name_or_addr)
            cell = snapshot.get_cell(name_or_addr)
            self.set_value(name_or_addr, cell.value)
        for name_or_addr in snapshot.diff.deleted_cells:
            logger.debug("Deleting", name_or_addr)
            in_heap = isinstance(name_or_addr, MemoryAddress)
            self.delete_var(name_or_addr, in_heap=in_heap)

    def add_var(self, name, _type, value, in_heap=False):
        # Create the correct var sprite
        var = create_variable_sprite(name, _type, value, vars_index=self.vars_by_name,
                                     in_heap=in_heap)
        # Select the correct blackboard and add&align the var
        if in_heap:
            blackboard = self.heap_blackboard
        else:
            blackboard = self.stack_blackboard
        blackboard.add_var(var)
        self.vars_by_name[name] = var

    def delete_var(self, name, in_heap):
        if not in_heap:
            raise NotImplementedError()
        var = self.vars_by_name[name]
        self.vars_by_name.pop(name)
        self.heap_blackboard.remove(var)

    def set_value(self, name, value):
        var = self.vars_by_name[name]
        var.set_value(value)

    def load_initial_snapshot(self, snapshot):
        self.process_snapshot(snapshot)
        # and now, refresh values, so pointers arrows are drawn correctly
        for name_or_addr in snapshot.diff.new_cells:
            var = self.vars_by_name[name_or_addr]
            if hasattr(var, "cached_value"):
                # make sure ComposedSprite is refreshed
                del var.cached_value
            cell = snapshot.get_cell(name_or_addr)
            var.set_value(cell.value)
