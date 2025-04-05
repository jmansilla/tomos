from logging import getLogger
from os import getenv

from skitso.scene import Scene
from skitso import movement

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
        super().__init__(configs.CANVAS_SIZE, output_path,
                         color=configs.CANVAS_COLOR,
                         file_extension=configs.FRAME_FILE_FORMAT)

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

        self.folder_path = Path(base_folder_path) / "frames"
        self.folder_path.mkdir(parents=True, exist_ok=True)

    def render(self, explicit_frames_only):
        memory_block = MemoryBlock(self.uses_heap, self.pointers_heap_to_heap)
        memory_block.z_index = 1
        self.add(memory_block)
        memory_block.shift(movement.RIGHT * (self.width / 2))
        if configs.MEMORY_BOARD_DISPLACEMENT:
            memory_block.shift(movement.RIGHT * configs.MEMORY_BOARD_DISPLACEMENT)

        code_block = TomosCode(self.source_code)
        code_block.center_respect_to(self)
        code_block.to_edge(self, movement.LEFT_EDGE)
        code_block.shift(movement.RIGHT * (configs.PADDING))
        self.add(code_block)

        loaded = self.timeline.loaded_initial_snapshot()
        if loaded:
            memory_block.load_initial_snapshot(loaded)

        shots_declarations = self.timeline.list_declaration_snapshots()
        for shot in shots_declarations:
            memory_block.process_snapshot(shot)
        shots_sentences = self.timeline.list_sentence_snapshots()
        if shots_sentences:
            code_block.mark_next_line(shots_sentences[0].line_number)
        # Initial tick. Empty canvas (or with imported state if loaded from file).
        self.tick()

        for i, shot in enumerate(shots_sentences):
            memory_block.process_snapshot(shot)
            code_block.mark_next_line(getattr(shot.next, "line_number", None))
            if not explicit_frames_only:
                self.tick()
            elif shot.explicit_checkpoint:
                self.tick()

            logger.info(f"Processing snapshot {i}")
            if STOP_AT == str(i):
                print("STOP at", i)
                break

        # Final tick. Always here.
        self.tick()

        number_of_generated_frames = self.next_tick_id
        return number_of_generated_frames
