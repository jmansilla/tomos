from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text

from skitso.atom import Container, Point
from skitso import movement
from skitso.shapes import Rectangle, RoundedRectangle, Arrow, DeadArrow


class Variable(Container):
    def get_color_by_type(self, _type):
        if isinstance(_type, type):
            type_name = _type.__name__
        else:
            type_name = type(_type).__name__
        if type_name in configs.COLOR_BY_TYPE:
            return configs.COLOR_BY_TYPE[type_name]
        else:
            return configs.UNNAMED_COLORS.pop()

    def __init__(self, name, _type, value, in_heap=False):
        super().__init__(Point(0, 0))  # created at origin. Needs to be shifted later.
        self.name = name    # for debugging.
        self._type = _type
        self.in_heap = in_heap
        self.color = self.get_color_by_type(_type)
        self.name_sprite = self.set_name(name)
        self.add(self.name_sprite)
        self.rect = self.build_box(0, self.name_sprite.box_height + configs.PADDING*.5)
        self.add(self.rect)
        self.set_value(value)

    def set_name(self, name):
        bold = not self.in_heap
        return build_text(str(name), bold=bold)

    def build_box(self, x, y):
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        rect = RoundedRectangle(
            x, y, width=w, height=h,
            fill_color=self.color, fill_opacity=0.45,
            stroke_width=2, stroke_color="white",
            corner_radius=7)
        return rect

    def set_value(self, value):
        new_value_sprite = self.build_value_sprite(value)
        old_value_sprite = getattr(self, 'value_sprite', None)  # shall be None only for the first time
        if old_value_sprite is not None:
            self.remove(self.value_sprite)
        self.value_sprite = new_value_sprite
        self.add(self.value_sprite)

    def build_value_sprite(self, value):
        value_sprite = build_text(str(value))
        value_sprite.center_respect_to(self.rect)
        # centering text in pillow is not so easy
        value_sprite.shift(movement.UP * value_sprite.box_height * .1)
        return value_sprite

    def point_to_receive_arrow(self):
        location = self.rect.position
        location.y += self.rect.box_height / 2
        return location


class PointerVar(Variable):

    def __init__(self, vars_index, *args, **kwargs):
        # in order to be able to draw arrows, need access to the vars_index
        self.vars_index = vars_index
        super().__init__(*args, **kwargs)

    @property
    def arrow_start_point(self):
        # returns x, y where arrows shall start
        location = self.rect.end
        location.y -= self.rect.box_height / 2
        return location

    @property
    def arrow_color(self):
        # ideally shall return a color based on the cell it points to
        return self.get_color_by_type(self._type.of)

    @property
    def tip_height(self):
        return 20 * configs.SCALE

    def build_dead_arrow(self):
        sp = self.arrow_start_point
        half_height = self.rect.box_height / 2
        return DeadArrow(sp.x, sp.y, half_height, self.tip_height, self.arrow_color, 2)

        # elbow_point = sp + (RIGHT * half_height)
        # end_point = elbow_point + (DOWN * half_height)

        # return DeadArrow(sp, elbow_point, end_point, self.tip_scale,
        #                  color=self.arrow_color, stroke_width=2)

    def build_arrow_to_var(self, var):
        x, y = self.arrow_start_point
        to_x, to_y = var.point_to_receive_arrow()
        arrow = Arrow(x, y, to_x, to_y, color=self.arrow_color,
                      thickness=2, tip_height=self.tip_height)
        return arrow

    def set_value(self, value):
        super().set_value(value)
        if not value in self.vars_index:
            new_arrow = self.build_dead_arrow()
        else:
            pointed_var = self.vars_index[value]
            new_arrow = self.build_arrow_to_var(pointed_var)
        old_arrow = getattr(self, 'arrow', None)  # shall be None only for the first time
        if old_arrow is not None:
            self.remove(self.arrow)
        self.arrow = new_arrow
        self.add(self.arrow)

