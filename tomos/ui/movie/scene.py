from logging import getLogger
from os import getenv

from skitso.scene import Scene
from skitso import movement

from tomos.ayed2.ast.sentences import Assignment, If, While
from tomos.ayed2.ast.program import TypeDeclaration, VarDeclaration
from tomos.ui.movie import configs
from tomos.ui.movie.panel.code import TomosCode
from tomos.ui.movie.panel.memory import MemoryBlock


logger = getLogger(__name__)
STOP_AT = getenv("STOP_AT", "")


class TomosScene(Scene):

    def __init__(self, source_code, timeline, output_path):
        self.source_code = source_code
        self.timeline = timeline
        super().__init__(configs.CANVAS_SIZE, output_path, color=configs.CANVAS_COLOR)

    def build_folder(self, base_folder_path):
        # Removing "NameOfSceneClass" from folder path, which is added by skitso
        from pathlib import Path
        self.folder_path = (
            Path(base_folder_path) / "frames"
        )
        self.folder_path.mkdir(parents=True, exist_ok=True)

    def render(self):
        memory_block = MemoryBlock()
        self.add(memory_block)
        memory_block.shift(movement.RIGHT * (self.width / 2))

        code_block = TomosCode(self.source_code)
        code_block.center_respect_to(self)
        code_block.to_edge(self, movement.LEFT_EDGE)
        code_block.shift(movement.RIGHT * (configs.PADDING))
        self.add(code_block)
        self.tick()

        for i, snapshot in enumerate(self.timeline.timeline):
            if isinstance(snapshot.last_sentence, TypeDeclaration):
                continue
            if isinstance(snapshot.last_sentence, VarDeclaration):
                memory_block.process_snapshot(snapshot)
                continue
            code_block.focus_line(snapshot.line_number)
            self.tick()

            if isinstance(snapshot.last_sentence, (If, While)):
                guard = snapshot.last_sentence.guard
                guard_value = snapshot.expression_values[guard]
                guard_hint = code_block.build_hint(guard_value)

            if isinstance(snapshot.last_sentence, Assignment):
                expr = snapshot.last_sentence.expr
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

