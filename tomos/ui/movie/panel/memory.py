from manim import VGroup, Rectangle, RoundedRectangle, Text, BOLD
from manim import LEFT, RIGHT, DOWN, UP

colors = {
    "IntType": "#A2D2DF",
    "BoolType": "#F6EFBD",
    "RealType": "##E4C087",
    "CharType": "#BC7C7C",
    }

unamed_colors = ["red", "blue", "orange", "purple", "white"]


class Variable(VGroup):
    box_scale = 2
    box_1_char_ratio = (0.4, 0.4)
    box_extra_char_ratio = (0.2, 0)  # to be added to box_1_char_ratio per extra char
    font_size_base = 12

    @property
    def font_size(self):
        return self.font_size_base * self.box_scale

    def __init__(self, name, _type, value, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        if str(_type) in colors:
            self.color = colors[str(_type)]
        else:
            self.color = unamed_colors.pop()

        self.rect = self.build_box()
        self.add(self.rect)

        self.name = Text(name, font="Monospace", font_size=self.font_size, weight=BOLD)
        self.name.align_to(self.rect, LEFT)
        self.name.align_to(self.rect, UP)
        self.name.shift(UP * 0.2 * self.box_scale)

        self.add(self.name)
        self.value = self.build_value_text(value)
        self.add(self.value)

    def build_box(self, extra_chars=0):
        w, h = Variable.box_1_char_ratio
        if extra_chars > 0:
            w += extra_chars * Variable.box_extra_char_ratio[0]
            h += extra_chars * Variable.box_extra_char_ratio[1]
        w *= Variable.box_scale
        h *= Variable.box_scale
        rect = RoundedRectangle(
            width=w, height=h,
            fill_color=self.color, fill_opacity=0.25,
            stroke_width=1, stroke_color=self.color,
            corner_radius=0.1)
        return rect

    def build_value_text(self, value):
        new_value = Text(str(value), font="Monospace", font_size=self.font_size)

        # moves value to be in the center of the box
        rect_h, rect_w = self.rect.height, self.rect.width
        val_h, val_w = new_value.height, new_value.width
        new_value.align_to(self.rect, LEFT)
        new_value.align_to(self.rect, UP)
        new_value.shift(DOWN * (rect_h/2 - val_h/2))
        new_value.shift(RIGHT * (rect_w/2 - val_w/2))
        return new_value


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

