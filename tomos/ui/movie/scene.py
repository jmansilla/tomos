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

    def render(self, explicit_frames_only):
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
        # Initial tick. Empty canvas (or with imported state if loaded from file).
        self.tick()

        # Iterate now snapshots until all Type & Var declarations are processed.
        at_least_one_declaration = False
        declarations_finished = False
        for i, snapshot in enumerate(tl):
            if isinstance(snapshot.last_executed, (TypeDeclaration, VarDeclaration)):
                at_least_one_declaration = True
                memory_block.process_snapshot(snapshot)
                continue
            if not declarations_finished:
                declarations_finished = True
                # All declarations finished. Let's tick that first.
                if at_least_one_declaration:
                    self.tick()
            code_block.focus_line(snapshot.line_number)  # always focus the last executed line
            memory_block.process_snapshot(snapshot)
            sentence = snapshot.last_executed
            if not explicit_frames_only:
                self.tick()
            elif sentence.get_parsing_metadata("checkpoint"):
                self.tick()

            logger.info(f"Processing snapshot {i}")
            if STOP_AT == str(i):
                print("STOP at", i)
                break

        # Final tick. Always here.
        code_block.focus_line(None)
        self.tick()

        number_of_generated_frames = self.next_tick_id
        return number_of_generated_frames

