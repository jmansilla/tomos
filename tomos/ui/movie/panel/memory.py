from manim import VGroup, Rectangle, Text
from manim import LEFT, RIGHT, DOWN, UP

colors = {
    "": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "blue": "#0000ff",
    "IntType": "#00ff00",
    "orange": "#ffa500",
    "purple": "#800080"}


unamed_colors = ["red", "blue", "orange", "purple", "white"]


class Variable(VGroup):

    def __init__(self, name, _type, value, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        if str(_type) in colors:
            self.color = colors[str(_type)]
        else:
            self.color = unamed_colors.pop()
        self.rect = Rectangle(width=1, height=0.25, fill_color=self.color, fill_opacity=0.5)
        self.name = Text(name, font="Monospace").scale(0.2)
        self.add(self.rect)
        self.name.align_to(self.rect, LEFT)
        self.name.align_to(self.rect, UP)
        self.add(self.name)
        self.name.shift(UP * 0.15)
        self.set_value(value)
        self.add(self.value)

    def set_value(self, value):
        self.value = Text(str(value), font="Monospace").scale(0.2)
        self.value.align_to(self.rect, LEFT)
        self.value.align_to(self.rect, UP)
        self.value.shift(DOWN * self.rect.height * 0.4)
        self.value.shift(RIGHT * 0.2)


class MemoryBlock(VGroup):

    def __init__(self, scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.space = Rectangle(width=7, height=4, color="black", fill_color="white", fill_opacity=0)
        self.add(self.space)
        self.space.next_to(self, RIGHT)
        self.vars_by_name = {}
        self.last_block = None
        self.animator = scene

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
        var.align_to(self.space, LEFT)
        if self.last_block is None:
            var.align_to(self.space, UP)
        else:
            var.align_to(self.last_block, DOWN)
            var.shift(DOWN * var.rect.height * 2.5)
        # var.shift(RIGHT * 0.25)
        self.space.add(var)
        self.last_block = var
        self.vars_by_name[name] = var

    def set_value(self, name, value):
        var = self.vars_by_name[name]
        if hasattr(var, 'value'):
            var.remove(var.value)
        var.set_value(value)
        var.add(var.value)

