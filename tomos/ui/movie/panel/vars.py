from copy import deepcopy

from tomos.ayed2.ast import types as ayed_types
from tomos.exceptions import CantDrawError
from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text

from skitso.atom import Container, Point
from skitso import movement
from skitso.shapes import Rectangle, RoundedRectangle, Arrow, DeadArrow

thickness = 2  #configs.THICKNESS


def create_variable_sprite(
        name, _type, value, vars_index=None, in_heap=False,
        inside_array=False):
    vars_index = vars_index or {}

    print('Estoy aca', inside_array)
    if _type.is_pointer:
        klass = PointerVarSprite
    elif isinstance(_type, ayed_types.ArrayOf):
        klass = ArraySprite
    else:
        klass = VariableSprite
    print('La clase seleccionada es', klass)
    if inside_array:
        class element_klass(ArrayElementMixin, klass):    # type: ignore
            pass
        klass = element_klass
    return klass(name, _type, value, vars_index, in_heap)  # type: ignore


class VariableSprite(Container):

    def __init__(self, name, _type, value, vars_index, in_heap=False):
        self.name = name    # for debugging.
        self._type = _type
        self.in_heap = in_heap
        self.vars_index = vars_index # for pointers, to be able to draw arrows
        self.color = self.get_color_by_type(_type)
        super().__init__(Point(0, 0))  # created at origin. Needs to be shifted later.
        dx, dy = self.add_name_sprite(name)
        self.rect = self.build_box(0 + dx, 0 + dy)
        self.set_value(value)

    def get_color_by_type(self, _type):
        if isinstance(_type, type):
            type_name = _type.__name__
        else:
            type_name = type(_type).__name__
        if type_name in configs.COLOR_BY_TYPE:
            return configs.COLOR_BY_TYPE[type_name]
        else:
            return configs.UNNAMED_COLORS.pop()

    def add_name_sprite(self, name):
        # Create the name sprite, adds it to self,
        # and returns (dx, dy) delta for value rect object
        self.name_sprite = build_text(str(name), bold=not self.in_heap)
        self.add(self.name_sprite)
        return 0, self.name_sprite.box_height + configs.PADDING*.5

    def build_box(self, x, y):
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        rect = RoundedRectangle(
            x, y, width=w, height=h,
            fill_color=self.color, fill_opacity=0.45,
            stroke_width=2, stroke_color="white",
            corner_radius=7)
        self.add(rect)
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
        x, y = self.rect.position
        y += self.rect.box_height / 2
        return Point(x, y)


class PointerVarSprite(VariableSprite):

    @property
    def arrow_start_point(self):
        # returns x, y where arrows shall start
        x, y = self.rect.end
        y -= self.rect.box_height / 2
        return Point(x, y)

    @property
    def arrow_color(self):
        # ideally shall return a color based on the cell it points to
        return "white"  #self.get_color_by_type(self._type.of)

    @property
    def tip_height(self):
        return 10 * configs.SCALE

    def build_dead_arrow(self):
        sp = self.arrow_start_point
        half_height = self.rect.box_height / 2
        return DeadArrow(sp.x, sp.y, half_height, self.tip_height, self.arrow_color, thickness)

    def build_arrow_to_var(self, var):
        x, y = self.arrow_start_point
        to_x, to_y = var.point_to_receive_arrow()
        arrow = Arrow(x, y, to_x, to_y, color=self.arrow_color,
                      thickness=thickness, tip_height=self.tip_height)
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


class ArrayElementMixin:

    def add_name_sprite(self, name):
        # do nothing
        return 0, 0


class ArraySprite(VariableSprite):
    # Assumptions:
    # - the array is of elements of a basic type, enum, pointer, or synonym of them.
    # - the array length is known, does not change, and it's bigger than 0.
    # - the array has a single dimension.

    def __init__(self, name, _type, value, vars_index, in_heap=False):
        self.check_is_drawable(_type, value)
        self.length = len(value)
        super().__init__(name, _type, value, vars_index, in_heap=in_heap)

    def check_is_drawable(self, _type, value):
        if not isinstance(_type, ayed_types.ArrayOf):
            raise CantDrawError(f"Cannot draw a '{type(_type)}' as an array.")
        of = _type.of
        while isinstance(of, ayed_types.Synonym):
            of = of.underlying_type
        if not isinstance(of, (ayed_types.PointerOf, ayed_types.Enum, ayed_types.BasicType)):
            raise CantDrawError(f"Cannot draw an array of type '{type(of)}'.")
        shape = _type.shape()
        if len(shape) != 1:
            raise CantDrawError(f"Cannot draw an array of shape '{shape}'.")
        if shape[0] != len(value):
            raise CantDrawError(f"Cannot draw an array with shape '{shape}' and value '{value}'.")

    def get_color_by_type(self, _type):
        return super().get_color_by_type(_type.of)

    def set_value(self, value):
        first_time = False
        if not hasattr(self, "cached_value"):
            self.cached_value = deepcopy(value)
            first_time = True
        for i, val in enumerate(value):
            if first_time or val != self.cached_value[i]:
                self.element_sprites[i].set_value(val)
                self.cached_value[i] = val

    def build_box(self, x, y):
        vertical = configs.ARRAY_ORIENTATION == "vertical"
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        if vertical:
            h *= self.length
        else:
            w *= self.length

        rect = Rectangle(x, y, w, h, fill_color=self.color,
                         stroke_color="gray", stroke_width=3)
        self.add(rect)

        self.element_sprites = []
        for i in range(self.length):
            name = f"{self.name}[{i}]"
            sub_var = create_variable_sprite(name, self._type.of, '--', self.vars_index,
                                         in_heap=self.in_heap, inside_array=True)
            self.element_sprites.append(sub_var)
            self.add(sub_var)
            sub_var.move_to(Point(x, y))
            if vertical:
                sub_var.shift(movement.DOWN * (i * sub_var.box_height))
            else:
                sub_var.shift(movement.RIGHT * (i * sub_var.box_width))
        return rect
