from manim import LEFT, RIGHT, DOWN, UP
from manim import VGroup, RoundedRectangle, Text, BOLD

from tomos.ui.movie import configs


class Variable(VGroup):
    box_scale = configs.SCALE
    box_1_char_ratio = (0.4, 0.4)
    box_extra_char_ratio = (0.2, 0)  # to be added to box_1_char_ratio per extra char
    font_size_base = configs.FONT_SIZE

    @property
    def font_size(self):
        return self.font_size_base * self.box_scale

    def __init__(self, name, _type, value, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        if str(_type) in configs.COLOR_BY_TYPE:
            self.color = configs.COLOR_BY_TYPE[str(_type)]
        else:
            self.color = configs.UNNAMED_COLORS.pop()

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