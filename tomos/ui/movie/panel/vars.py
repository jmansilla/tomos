from manim import LEFT, RIGHT, DOWN, UP, BOLD
from manim import VGroup, RoundedRectangle, Arrow, CurvedArrow, StealthTip

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
        self.raw_name = name    # for debugging. Raw for opposite of the sprite name
        self.raw_value = value  # for debugging. Raw for opposite of the sprite value
        self._type = _type
        self.in_heap = in_heap
        self.color = self.get_color_by_type(_type)
        self.rect = self.build_box()
        self.add(self.rect)
        self.set_name(name)
        self.set_value(value)

    def set_name(self, name):
        # cant change the weight of the text after creation, thats why the if
        if self.in_heap:
            self.name_sprite = build_text(str(name))
        else:
            self.name_sprite = build_text(name, weight=BOLD)
        self.name_sprite.align_to(self.rect, LEFT)
        self.name_sprite.align_to(self.rect, UP)
        self.name_sprite.shift(UP * 0.2 * configs.SCALE)
        self.add(self.name_sprite)

    def build_box(self):
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        rect = FlexWidthRoundedRectangle(
            width=w, height=h,
            fill_color=self.color, fill_opacity=0.45,
            stroke_width=1, stroke_color=self.color,
            corner_radius=0.1 * configs.SCALE)
        return rect

    def set_value(self, value, transition_animator=None):
        new_value_sprite = self.build_value_sprite(value)
        old_value_sprite = getattr(self, 'value_sprite', None)  # shall be None only for the first time
        animator = getattr(transition_animator, 'animate_value_change', None)
        if animator is not None and old_value_sprite is not None:
            animator(self, old_value_sprite, new_value_sprite)

        if old_value_sprite is not None:
            self.remove(self.value_sprite)
        self.value_sprite = new_value_sprite
        self.add(self.value_sprite)

    def build_value_sprite(self, value):
        value_sprite = build_text(str(value))
        # move it to be in the center of the box
        rect_h, rect_w = self.rect.height, self.rect.width
        val_h, val_w = value_sprite.height, value_sprite.width
        value_sprite.align_to(self.rect, LEFT)
        value_sprite.align_to(self.rect, UP)
        value_sprite.shift(DOWN * (rect_h/2 - val_h/2))
        value_sprite.shift(RIGHT * (rect_w/2 - val_w/2))
        return value_sprite

    def point_to_receive_arrow(self):
        location = self.rect.get_center()
        return location + LEFT * (self.rect.width / 2)


class PointerVar(Variable):

    def __init__(self, vars_index, *args, **kwargs):
        # in order to be able to draw arrows, need access to the vars_index
        self.vars_index = vars_index
        super().__init__(*args, **kwargs)

    def arrow_start_point(self):
        # returns x, y, z where arrows shall start
        center = self.rect.get_center()
        return center + RIGHT * (self.rect.width / 2)

    @property
    def arrow_color(self):
        # ideally shall return a color based on the cell it points to
        return self.get_color_by_type(self._type.of)

    def build_dead_arrow(self):
        sp = self.arrow_start_point()
        half_height = self.rect.height / 2
        end_point = sp + (DOWN * half_height * 1.5)
        end_point += (RIGHT * half_height)
        arrow = CurvedArrow(sp, end_point, tip_shape=StealthTip,
                            color=self.arrow_color, radius=-half_height*1.2)
        arrow.tip.scale(0.125 * configs.SCALE)
        return arrow

    def build_arrow_to_var(self, var):
        sp = self.arrow_start_point()
        end_point = var.point_to_receive_arrow()
        arrow = Arrow(sp, end_point, tip_shape=StealthTip, color=self.arrow_color)
        arrow.tip.scale(0.125 * configs.SCALE)
        return arrow

    def set_value(self, value, transition_animator=None):
        super().set_value(value, transition_animator)
        if not value in self.vars_index:
            new_arrow = self.build_dead_arrow()
        else:
            pointed_var = self.vars_index[value]
            new_arrow = self.build_arrow_to_var(pointed_var)
        old_arrow = getattr(self, 'arrow', None)  # shall be None only for the first time
        animator = getattr(transition_animator, 'animate_arrow_change', None)
        if animator is not None and old_arrow is not None:
            animator(self, old_arrow, new_arrow)

        if old_arrow is not None:
            self.remove(self.arrow)
        self.arrow = new_arrow
        self.add(self.arrow)



