from logging import getLogger
from os import getenv

from skitso.scene import Scene
from skitso import movement

from tomos.ayed2.ast.sentences import Assignment, If, While
from tomos.ayed2.ast.program import TypeDeclaration, VarDeclaration
from tomos.ayed2.evaluation.state import MemoryAddress
from tomos.ui.movie import configs
from tomos.ui.movie.panel.code import TomosCode
from tomos.ui.movie.panel.memory import MemoryBlock

logger = getLogger(__name__)
STOP_AT = getenv("STOP_AT", "")


class TomosScene(Scene):

    def __init__(self, source_code, timeline, output_path):
        self.source_code = source_code
        self.timeline = timeline
        self.uses_heap = False
        self.pointers_heap_to_heap = False
        self.extract_configs_from_timeline()
        super().__init__(configs.CANVAS_SIZE, output_path, color=configs.CANVAS_COLOR)

    def extract_configs_from_timeline(self):
        def check_cell_is_or_contains_pointer(cell):
            if cell.var_type.is_pointer:
                return True
            elif hasattr(cell, "sub_cells"):
                scs = cell.sub_cells
                if isinstance(scs, dict):
                    scs = list(scs.values())
                return any(check_cell_is_or_contains_pointer(sc) for sc in scs)

        for snapshot in self.timeline.timeline:
            for name_or_addr in snapshot.diff.new_cells:
                if isinstance(name_or_addr, MemoryAddress):
                    self.uses_heap = True
                    cell = snapshot.state.heap[name_or_addr]
                    if check_cell_is_or_contains_pointer(cell):
                        self.pointers_heap_to_heap = True
                        return  # no need to continue

    def build_folder(self, base_folder_path):
        # Removing "NameOfSceneClass" from folder path, which is added by skitso
        from pathlib import Path
        self.folder_path = (
            Path(base_folder_path) / "frames"
        )
        self.folder_path.mkdir(parents=True, exist_ok=True)

    def render(self):
        memory_block = MemoryBlock(self.uses_heap, self.pointers_heap_to_heap)
        memory_block.z_index = 1
        self.add(memory_block)
        memory_block.shift(movement.RIGHT * (self.width / 2))

        code_block = TomosCode(self.source_code)
        code_block.center_respect_to(self)
        code_block.to_edge(self, movement.LEFT_EDGE)
        code_block.shift(movement.RIGHT * (configs.PADDING))
        self.add(code_block)

        tl = self.timeline.timeline
        if tl and tl[0].last_executed == self.timeline.STATE_LOADED_FROM_FILE:
            initial_snapshot = tl.pop(0)
            memory_block.load_initial_snapshot(initial_snapshot)
        self.tick()

        for i, snapshot in enumerate(tl):
            if isinstance(snapshot.last_executed, TypeDeclaration):
                continue
            if isinstance(snapshot.last_executed, VarDeclaration):
                memory_block.process_snapshot(snapshot)
                continue
            code_block.focus_line(snapshot.line_number)
            self.tick()

            if isinstance(snapshot.last_executed, (If, While)):
                guard = snapshot.last_executed.guard
                guard_value = snapshot.expression_values[guard]
                guard_hint = code_block.build_hint(guard_value)

            if isinstance(snapshot.last_executed, Assignment):
                expr = snapshot.last_executed.expr
                expr_value = snapshot.expression_values[expr]
                expr_hint = code_block.build_hint(expr_value)

            memory_block.process_snapshot(snapshot)

            logger.info(f"Processing snapshot {i}")
            if STOP_AT == str(i):
                print("STOP at", i)
                break
        code_block.focus_line(None)
        self.tick()

        number_of_generated_frames = self.next_tick_id
        return number_of_generated_frames

