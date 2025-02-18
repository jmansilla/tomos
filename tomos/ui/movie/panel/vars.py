from copy import deepcopy

from tomos.ayed2.ast import types as ayed_types
from tomos.ayed2.ast.types.enum import EnumConstant
from tomos.exceptions import CantDrawError
from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text

from skitso.atom import Container, Point
from skitso import movement
from skitso.shapes import Rectangle, RoundedRectangle, Arrow, DeadArrow

thickness = 2  #configs.THICKNESS


class ColorAssigner:
    cache = deepcopy(configs.COLOR_BY_TYPE)

    @classmethod
    def get(cls, _type):
        if isinstance(_type, type):
            type_name = _type.__name__
        else:
            type_name = type(_type).__name__
        if type_name in cls.cache:
            return cls.cache[type_name]
        else:
            new_color = configs.UNNAMED_COLORS.pop()
            cls.cache[type_name] = new_color
            return new_color


def create_variable_sprite(
        name, _type, value, vars_index=None, in_heap=False,
        mixin_to_use=None):
    vars_index = vars_index or {}

    while isinstance(_type, ayed_types.Synonym):
        _type = _type.underlying_type

    if _type.is_pointer:
        klass = PointerVarSprite
    elif isinstance(_type, ayed_types.ArrayOf):
        klass = ArraySprite
    elif isinstance(_type, ayed_types.Tuple):
        klass = TupleSprite
    else:
        klass = VariableSprite
    if mixin_to_use:
        class element_klass(mixin_to_use, klass):    # type: ignore
            pass
        klass = element_klass
    return klass(name, _type, value, vars_index, in_heap)  # type: ignore


class SubVarMixin:

    def add_name_sprite(self, name):
        if isinstance(name, int):
            name = '[%d]' % name
        max_len = configs.TUPLE_FIELD_NAME_MAX_LEN
        name = str(name)
        if len(name) > max_len:
            name = name[:max_len] + "…"
        self.name_sprite = build_text(str(name), bold=not self.in_heap)  # type: ignore
        self.add(self.name_sprite)  # type: ignore
        return self.name_sprite.box_width + configs.PADDING / 2, 0

    def shift_rect_and_value(self, vector):
        self.rect.shift(vector)  # type: ignore
        self.value_sprite.shift(vector)  # type: ignore

    def get_stroke_with_and_color(self):
        return 1, "gray"


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
        return ColorAssigner.get(_type)

    def add_name_sprite(self, name):
        # Create the name sprite, adds it to self,
        # and returns (dx, dy) delta for value rect object
        self.name_sprite = build_text(str(name), bold=not self.in_heap)
        self.add(self.name_sprite)
        return 0, self.name_sprite.box_height + configs.PADDING*.5

    def get_stroke_with_and_color(self):
        return 2, "white"

    def build_box(self, x, y):
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        stk_width, stk_color = self.get_stroke_with_and_color()
        rect = RoundedRectangle(
            x, y, width=w, height=h,
            fill_color=self.color, fill_opacity=0.45,
            stroke_width=stk_width, stroke_color=stk_color,
            corner_radius=7)
        self.add(rect)
        return rect

    def set_value(self, value):
        if isinstance(value, EnumConstant):
            value = value.name
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


class ComposedSprite(VariableSprite):

    def __init__(self, name, _type, value, vars_index, in_heap=False):
        self.check_is_drawable(_type, value)
        self.length = len(value)
        super().__init__(name, _type, value, vars_index, in_heap=in_heap)

    def check_is_drawable(self, _type, value):
        raise NotImplementedError

    def vertical_orientation(self):
        raise NotImplementedError

    @property
    def margin(self):
        return configs.PADDING / 2

    def build_box(self, x, y):
        vertical = self.vertical_orientation()
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        if vertical:
            h *= self.length
        else:
            w *= self.length

        m2 = self.margin * 2
        rect = Rectangle(x, y, w + m2, h + m2, fill_color=self.color,
                         stroke_color="gray", stroke_width=1)
        self.add(rect)
        self.rect = rect
        self.build_subsprites(x, y, vertical)
        return rect

    def iterate_fields(self):
        raise NotImplementedError

    def set_value(self, value):
        # asumes that value is a dict
        first_time = False
        if not hasattr(self, "cached_value"):
            self.cached_value = deepcopy(value)
            first_time = True
        for k, val in value.items():
            if first_time or val != self.cached_value[k]:
                self.element_sprites[k].set_value(val)  # type: ignore
                self.cached_value[k] = val

    def build_subsprites(self, x, y, vertical):
        x, y = x + self.margin, y + self.margin
        self.element_sprites = {}
        max_x = 0
        for i, (fname, ftype) in enumerate(self.iterate_fields()):
            sub_var = create_variable_sprite(fname, ftype, '--', self.vars_index,
                                         in_heap=self.in_heap,
                                         mixin_to_use=SubVarMixin)
            self.element_sprites[fname] = sub_var
            self.add(sub_var)
            sub_var.move_to(Point(x, y))
            if vertical:
                sub_var.shift(movement.DOWN * (i * sub_var.box_height))
            else:
                sub_var.shift(movement.RIGHT * (i * sub_var.box_width))
            max_x = max(max_x, sub_var.rect.position.x)

        # and now, adjust the alignment
        max_delta = 0
        for sub_var in self.element_sprites.values():
            if sub_var.rect.position.x < max_x:
                delta = max_x - sub_var.rect.position.x
                max_delta = max(delta, max_delta)
                vector = movement.RIGHT * delta
                sub_var.shift_rect_and_value(vector)
        if max_x > 0:
            self.rect.width += max_x


class ArraySprite(ComposedSprite):
    # Assumptions:
    # - the array is of elements of a basic type, enum, pointer, or synonym of them.
    # - the array length is known, does not change, and it's bigger than 0.
    # - the array has a single dimension.

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

    def set_value(self, value):
        as_dict = {i:v for i, v in enumerate(value)}
        super().set_value(as_dict)

    def vertical_orientation(self):
        return configs.ARRAY_ORIENTATION == "vertical"

    def iterate_fields(self):
        for i in range(self.length):
            yield i, self._type.of


class TupleSprite(ComposedSprite):
    # Assumptions:
    # - tuple fields are of basic type, enum, pointer, or synonym of them.

    def check_is_drawable(self, _type, value):
        if not isinstance(_type, ayed_types.Tuple):
            raise CantDrawError(f"Cannot draw a '{type(_type)}' as a tuple.")

        for fname, ftype in _type.fields_mapping.items():
            while isinstance(ftype, ayed_types.Synonym):
                ftype = ftype.underlying_type
            if not isinstance(ftype, (ayed_types.PointerOf, ayed_types.Enum, ayed_types.BasicType)):
                raise CantDrawError(f"Cannot draw an tuple with field of type '{type(ftype)}'.")

        if len(_type.fields_mapping) != len(value):
            raise CantDrawError(f"Cannot draw a tuple with fields '{_type.fields_mapping}' and value '{value}'.")

    def vertical_orientation(self):
        return configs.TUPLE_ORIENTATION == "vertical"

    def iterate_fields(self):
        for fname, ftype in self._type.fields_mapping.items():
            yield fname, ftype

