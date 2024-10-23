from manim import LEFT, RIGHT, DOWN, UP, BOLD
from manim import VGroup, RoundedRectangle, CurvedArrow, StealthTip

from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text


class FlexWidthRoundedRectangle(RoundedRectangle):
    def __init__(self, **kwargs):
        self._value_txt = str(kwargs.pop('value', ''))
        super().__init__(**kwargs)
        self.stretch_to_fit_width(self.suggested_width(self._value_txt))

    def suggested_width(self, value_txt=''):
        base_w = configs.VAR_BOX_MIN_CHAR_RATIO[0]
        extra_chars = max(0, len(value_txt) - configs.VAR_MAX_CHARS_MIN_BOX)
        w = base_w + extra_chars * configs.VAR_BOX_EXTRA_CHAR_RATIO[0]
        return w * configs.SCALE


class Variable(VGroup):
    def get_color_by_type(self, _type):
        if isinstance(_type, type):
            type_name = _type.__name__
        else:
            type_name = type(_type).__name__
        if type_name in configs.COLOR_BY_TYPE:
            return configs.COLOR_BY_TYPE[type_name]
        else:
            return configs.UNNAMED_COLORS.pop()

    def __init__(self, name, _type, value, in_heap=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self._type = _type
        self.in_heap = in_heap
        self.color = self.get_color_by_type(_type)
        self.rect = self.build_box()
        self.add(self.rect)

        # cant change the weight of the text after creation, thats why the if
        if in_heap:
            self.name = build_text(name, weight=BOLD)
        else:
            self.name = build_text(name)
        self.name.align_to(self.rect, LEFT)
        self.name.align_to(self.rect, UP)
        self.name.shift(UP * 0.2 * configs.SCALE)

        self.add(self.name)
        self.value = self.build_value_text(value)
        self.add(self.value)

    def build_box(self):
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        rect = FlexWidthRoundedRectangle(
            width=w, height=h,
            fill_color=self.color, fill_opacity=0.25,
            stroke_width=1, stroke_color=self.color,
            corner_radius=0.1)
        return rect

    def build_value_text(self, value):
        new_value = build_text(str(value))
        # self.animate(self.rect.set_width(self.rect.suggested_width(str(value))))

        # moves value to be in the center of the box
        rect_h, rect_w = self.rect.height, self.rect.width
        val_h, val_w = new_value.height, new_value.width
        new_value.align_to(self.rect, LEFT)
        new_value.align_to(self.rect, UP)
        new_value.shift(DOWN * (rect_h/2 - val_h/2))
        new_value.shift(RIGHT * (rect_w/2 - val_w/2))
        return new_value


class PointerVar(Variable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_dead_arrow()

    def arrow_start_point(self):
        # returns x, y, z where arrows shall start
        center = self.rect.get_center()
        return center + RIGHT * (self.rect.width / 2)

    def arrow_color(self):
        # ideally shall return a color based on the cell it points to
        return self.get_color_by_type(self._type.of)

    def build_dead_arrow(self):
        sp = self.arrow_start_point()
        half_height = self.rect.height / 2
        end_point = sp + (DOWN * half_height)
        end_point += (RIGHT * half_height)
        self.arrow = CurvedArrow(sp, end_point, tip_shape=StealthTip,
                                 color=self.arrow_color(), radius=-half_height)
        self.arrow.tip.scale(0.5)
        self.add(self.arrow)
