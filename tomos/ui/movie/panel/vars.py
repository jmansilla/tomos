import colorsys
from copy import deepcopy

from PIL import ImageColor
from skitso.atom import Container, Point
from skitso import movement
from skitso.shapes import Rectangle, RoundedRectangle, Arrow

from tomos.ayed2.ast import types as ayed_types
from tomos.ayed2.ast.types.enum import EnumConstant
from tomos.exceptions import CantDrawError
from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text
from tomos.ui.movie.panel.pointer_arrows import DeadArrow, NullArrow, HeapToHeapArrowManager

thickness = configs.THICKNESS


class Switch:
    def __init__(self):
        self._state = True

    def turn_on(self):
        self._state = True

    def turn_off(self):
        self._state = False

    def flip(self):
        self._state = not self._state

    @property
    def is_on(self):
        return self._state


HIGHLIGHTING_SWITCH = Switch()


class ColorAssigner:
    cache = deepcopy(configs.COLOR_BY_TYPE)

    @classmethod
    def get_color(cls, _type):
        # synonyms are ignored
        if isinstance(_type, ayed_types.Synonym):
            _type = _type.underlying_type_closure()
        if isinstance(_type, ayed_types.ArrayOf):
            return cls.get_color("ArrayOf")
        if isinstance(_type, ayed_types.Tuple):
            return cls.get_color("Tuple")

        type_name = str(_type)
        if type_name in cls.cache:
            return cls.cache[type_name]
        else:
            pointer, pointed_type = cls.is_pointer_of(_type)
            if pointer:
                orig = cls.get_color(pointed_type)
                darkened = cls.darken_it(orig)
                cls.cache[type_name] = darkened
                return darkened
            new_color = configs.UNNAMED_COLORS[0]
            if len(configs.UNNAMED_COLORS) > 1:
                configs.UNNAMED_COLORS.pop(0)
            cls.cache[type_name] = new_color
            return new_color

    @classmethod
    def is_pointer_of(cls, _type):
        # We will only return True if its a Pointer (and not a Synonym of a pointer)
        # Returns boolean (true/false), and the pointed-type
        if isinstance(_type, ayed_types.PointerOf):
            return True, _type.of
        else:
            return False, None

    @classmethod
    def darken_it(cls, color, amount=0.2, smooth=True):
        as_ints = ImageColor.getcolor(color, "RGB")
        rgb_as_float = [x / 255 for x in as_ints]  # type: ignore
        hls = colorsys.rgb_to_hls(*rgb_as_float)  # type: ignore
        while smooth and amount > 0.05 and hls[1] <= amount * 2:
            # if color has low ligth, reduce the darkening
            amount = amount - 0.05
        dhls = (hls[0], max(0, hls[1] - amount), hls[2])
        darken = colorsys.hls_to_rgb(*dhls)
        d_rgb = [int(x * 255) for x in darken]  # type: ignore
        return "#{:02x}{:02x}{:02x}".format(*d_rgb)


def create_variable_sprite(name, _type, value, vars_index, in_heap=False, mixin_to_use=None):

    if isinstance(_type, ayed_types.Synonym):
        _type = _type.underlying_type_closure()

    if _type.is_pointer:
        klass = PointerVarSprite
    elif isinstance(_type, ayed_types.ArrayOf):
        klass = ArraySprite
    elif isinstance(_type, ayed_types.Tuple):
        klass = TupleSprite
    else:
        klass = VariableSprite
    if mixin_to_use:

        class element_klass(mixin_to_use, klass):  # type: ignore
            pass

        klass = element_klass
    return klass(name, _type, value, vars_index, in_heap)  # type: ignore


class SubVarMixin:

    def add_name_sprite(self, name):
        if isinstance(name, int):
            name = "[%d]" % name
        max_len = configs.TUPLE_FIELD_NAME_MAX_LEN
        name = str(name)
        if len(name) > max_len:
            name = name[:max_len] + "…"
        self.name_sprite = build_text(str(name), color="black")  # type: ignore

        self.add(self.name_sprite)  # type: ignore
        return self.name_sprite.box_width + configs.PADDING / 2, 0

    def shift_alignment(self, vector, nesting=0):
        # This function is call when there's a need to apply
        # some alignment so all sub-sprites and its names are tidy organized.
        self.rect.shift(vector)  # type: ignore
        if nesting > 0:
            self.name_sprite.shift(vector)
        if hasattr(self, "value_sprite"):
            self.value_sprite.shift(vector)  # type: ignore
        elif hasattr(self, "subsprites"):
            for sub_var in self.subsprites.values():  # type: ignore
                sub_var.shift_alignment(vector, nesting + 1)
        else:
            raise NotImplementedError

    def get_stroke_with_and_color(self):
        return 1, "gray"


class VariableSprite(Container):

    def __init__(self, name, _type, value, vars_index, in_heap=False):
        self.name = name  # for debugging.
        self._type = _type
        self.in_heap = in_heap
        self.vars_index = vars_index  # for pointers, to be able to draw arrows
        self.color = self.get_color_by_type(_type)
        super().__init__(Point(0, 0))  # created at origin. Needs to be shifted later.
        dx, dy = self.add_name_sprite(name)
        self.rect = self.build_box(0 + dx, 0 + dy)
        self.set_value(value)

    def get_color_by_type(self, _type):
        return ColorAssigner.get_color(_type)

    def add_name_sprite(self, name):
        # Create the name sprite, adds it to self,
        # and returns (dx, dy) delta for value rect object
        self.name_sprite = build_text(str(name))
        self.add(self.name_sprite)
        return 0, self.name_sprite.box_height + configs.PADDING * 0.5

    def get_stroke_with_and_color(self):
        return 2, "white"

    def build_box(self, x, y):
        w, h = configs.VAR_BOX_MIN_CHAR_RATIO
        w *= configs.SCALE
        h *= configs.SCALE
        stk_width, stk_color = self.get_stroke_with_and_color()
        rect = RoundedRectangle(
            x,
            y,
            width=w,
            height=h,
            fill_color=self.color,
            fill_opacity=0.45,
            stroke_width=stk_width,
            stroke_color=stk_color,
            corner_radius=7,
        )
        self.add(rect)
        return rect

    def set_value(self, value):
        if isinstance(value, EnumConstant):
            value = value.name
        new_value_sprite = self.build_value_sprite(value)
        old_value_sprite = getattr(
            self, "value_sprite", None
        )  # shall be None only for the first time
        if old_value_sprite is not None:
            self.remove(self.value_sprite)
        self.value_sprite = new_value_sprite
        if HIGHLIGHTING_SWITCH.is_on:
            self.value_sprite.is_highlighted = True  # type: ignore
        self.add(self.value_sprite)

    def build_value_sprite(self, value):
        value_sprite = build_text(str(value), highlightable=True)
        value_sprite.center_respect_to(self.rect)
        # centering text in pillow is not so easy
        value_sprite.shift(movement.UP * value_sprite.box_height * 0.1)
        return value_sprite

    def point_to_receive_arrow(self, heap_to_heap=False):
        if heap_to_heap:
            x, y = self.name_sprite.end
            y -= self.name_sprite.box_height * 0.55
            x += configs.PADDING / 2
            return Point(x, y)
        x, y = self.rect.position
        y += self.rect.box_height / 2
        return Point(x, y)


class PointerVarSprite(VariableSprite):
    heap_arrow_manager = HeapToHeapArrowManager(
        offset_step=configs.POINTER_HEAP_ARROW_OFFSET
    )

    @property
    def arrow_start_point(self):
        # returns x, y where arrows shall start
        x, y = self.rect.end
        y -= self.rect.box_height / 2
        return Point(x, y)

    @property
    def arrow_color(self):
        return configs.POINTER_ARROW_COLOR

    @property
    def tip_height(self):
        return 10 * configs.SCALE

    def build_dead_arrow(self):
        sp = self.arrow_start_point
        length = self.rect.box_height
        return DeadArrow(sp.x, sp.y, length, self.tip_height, configs.DEAD_ARROW_COLOR, thickness)

    def build_null_arrow(self):
        sp = self.arrow_start_point
        half_height = self.rect.box_height / 2
        return NullArrow(sp.x, sp.y, half_height, self.tip_height, self.arrow_color, thickness)

    def build_arrow_to_var(self, var):
        x, y = self.arrow_start_point
        to_x, to_y = var.point_to_receive_arrow(heap_to_heap=self.in_heap)
        if self.in_heap:
            arrow = self.heap_arrow_manager.add_arrow(
                x, y, to_x, to_y, self.arrow_color, thickness, self.tip_height
            )
        else:
            arrow = Arrow(
                x,
                y,
                to_x,
                to_y,
                color=self.arrow_color,
                thickness=thickness,
                tip_height=self.tip_height,
            )
        return arrow

    def set_value(self, value):
        super().set_value(value)
        if isinstance(value, ayed_types.NullValue):
            new_arrow = self.build_null_arrow()
        elif not value in self.vars_index:
            new_arrow = self.build_dead_arrow()
        else:
            pointed_var = self.vars_index[value]
            new_arrow = self.build_arrow_to_var(pointed_var)
        old_arrow = getattr(self, "arrow", None)  # shall be None only for the first time
        if old_arrow is not None:
            self.heap_arrow_manager.remove_arrow_if_heap_to_heap(old_arrow)
            self.remove(self.arrow)
        self.arrow = new_arrow
        self.add(self.arrow)


class ComposedSprite(VariableSprite):

    def __init__(self, name, _type, value, vars_index, in_heap=False):
        self.check_is_drawable(_type, value)
        self.length = len(value)
        self.cached_value = deepcopy(value)
        self.need_to_initialize_sub_sprites = True
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

        rect = Rectangle(
            x,
            y,
            w + self.margin,
            h + self.margin * 2,
            fill_color=self.color,
            stroke_color="gray",
            stroke_width=1,
        )
        self.add(rect)
        self.rect = rect
        self.build_subsprites(x, y, vertical)
        return rect

    def iterate_fields(self):
        raise NotImplementedError

    def set_value(self, value):
        # asumes that value is a dict
        first_time = self.need_to_initialize_sub_sprites
        for k, val in value.items():
            if first_time or val != self.cached_value[k]:
                self.subsprites[k].set_value(val)  # type: ignore
                self.cached_value[k] = val
        self.need_to_initialize_sub_sprites = False

    def build_subsprites(self, x, y, vertical):
        self.subsprites = {}
        # when orientation is vertical, we need to adjust the position of the subsprites
        # so that they are aligned. That's why we need to keep track of the maximum start x
        max_start_x = 0
        next_x, next_y = x + self.margin, y + self.margin
        for i, (fname, ftype) in enumerate(self.iterate_fields()):
            sub_value = self.cached_value[fname]
            sub_var = create_variable_sprite(
                fname, ftype, sub_value, self.vars_index, in_heap=self.in_heap, mixin_to_use=SubVarMixin
            )
            self.subsprites[fname] = sub_var
            self.add(sub_var)
            sub_var.move_to(Point(next_x, next_y))
            if vertical:
                next_y += sub_var.box_height + self.margin
            else:
                next_x += sub_var.box_width + self.margin
            max_start_x = max(max_start_x, sub_var.rect.position.x)
        last_sub_var = sub_var

        if vertical and max_start_x > 0:
            # and now, adjust the alignment of the subsprites,
            # and correct the size of the bounding box
            max_end_x = 0
            for sub_var in self.subsprites.values():
                if sub_var.rect.position.x < max_start_x:
                    delta = max_start_x - sub_var.rect.position.x
                    vector = movement.RIGHT * delta
                    sub_var.shift_alignment(vector)
                max_end_x = max(max_end_x, sub_var.end.x)
            self.rect.width = max_end_x + self.margin - self.rect.position.x
            self.rect.height = last_sub_var.rect.end.y + self.margin - self.rect.position.y
        else:
            # this actually needs to be implemented.
            pass


class ArraySprite(ComposedSprite):
    # Assumptions:
    # - the array is of elements of a basic type, enum, pointer, or synonym of them.
    # - the array length is known, does not change, and it's bigger than 0.
    # - the array has a single dimension.

    def check_is_drawable(self, _type, value):
        if not isinstance(_type, ayed_types.ArrayOf):
            raise CantDrawError(f"Cannot draw a '{type(_type)}' as an array.")
        of = _type.of
        if isinstance(of, ayed_types.Synonym):
            of = of.underlying_type_closure()
        if not isinstance(of, (ayed_types.PointerOf, ayed_types.Enum, ayed_types.BasicType)):
            raise CantDrawError(f"Cannot draw an array of type '{type(of)}'.")
        shape = _type.shape()
        if len(shape) != 1:
            raise CantDrawError(f"Cannot draw an array of shape '{shape}'.")
        if shape[0] != len(value):
            raise CantDrawError(f"Cannot draw an array with shape '{shape}' and value '{value}'.")

    def set_value(self, value):
        as_dict = {i: v for i, v in enumerate(value)}
        super().set_value(as_dict)

    def vertical_orientation(self):
        return configs.ARRAY_ORIENTATION == "vertical"

    def iterate_fields(self):
        for i in range(self.length):
            yield i, self._type.of


class TupleSprite(ComposedSprite):
    # Assumptions:
    # - tuple fields are of basic type, enum, pointer, or synonym of them.

    def check_is_drawable(self, _type, value):
        if not isinstance(_type, ayed_types.Tuple):
            raise CantDrawError(f"Cannot draw a '{type(_type)}' as a tuple.")

        allowed_sub_types = (ayed_types.PointerOf, ayed_types.Enum, ayed_types.BasicType,
                             ayed_types.ArrayOf)
        for fname, ftype in _type.fields_mapping.items():
            if isinstance(ftype, ayed_types.Synonym):
                ftype = ftype.underlying_type_closure()
            if not isinstance(ftype, allowed_sub_types):
                raise CantDrawError(f"Cannot draw a tuple with field of type '{type(ftype)}'.")

        if len(_type.fields_mapping) != len(value):
            raise CantDrawError(
                f"Cannot draw a tuple with fields '{_type.fields_mapping}' and value '{value}'."
            )

    def vertical_orientation(self):
        return configs.TUPLE_ORIENTATION == "vertical"

    def iterate_fields(self):
        for fname, ftype in self._type.fields_mapping.items():
            yield fname, ftype
