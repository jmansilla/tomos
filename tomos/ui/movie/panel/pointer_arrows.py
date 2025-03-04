from skitso.atom import Container, Point, BaseImgElem
from skitso.shapes import Arrow, Line

from tomos.ui.movie import configs


class RoundChamfer(BaseImgElem):
    # Given two lines crossing, a RoundChamfer is a quarter circle chamfering the corner
    # between the two lines.
    # The quadrant argument respects the following chart
    #    1   |   2
    #    ---------
    #    3   |   4

    def __init__(self, x, y, quadrant, radius, color, thickness):
        assert quadrant in [1, 2, 3, 4]
        super().__init__(Point(x, y))
        self.quadrant = quadrant
        self.radius = radius
        self.color = color
        self.thickness = thickness

    @property
    def end(self):
        # This is actually a non-sense implementation. Given that I'm not interested
        # on the end of a chamfer, I just return the position. But need to be fixed.
        return self.position

    def arc_center(self):
        x, y = self.position
        r = self.radius
        if self.quadrant == 1 or self.quadrant == 2:
            y -= r
        else:
            y += r

        if self.quadrant == 1 or self.quadrant == 3:
            x -= r
        else:
            x += r
        return (x, y)

    def arc_angles(self):
        if self.quadrant == 1:
            start_angle = 0
            end_angle = 90
        elif self.quadrant == 2:
            start_angle = 90
            end_angle = 180
        elif self.quadrant == 3:
            start_angle = 270
            end_angle = 360
        elif self.quadrant == 4:
            start_angle = 180
            end_angle = 270
        return start_angle, end_angle

    def draw_me(self, pencil, relative_to=None):
        x, y = self.arc_center()
        r = self.radius
        box = [(x - r, y - r), (x + r, y + r)]
        start_angle, end_angle = self.arc_angles()
        pencil.arc(box, start_angle, end_angle, fill=self.color, width=self.thickness)

    def delta_to_crossed_lines(self):
        # Considering that the center point is an intersection between a vertical and horizontal line,
        # return (dhx, dvy) values that should be added to the end point of such lines after
        # the chamfer is drawn
        corner_x, corner_y = self.position
        center_x, center_y = self.arc_center()
        return (center_x - corner_x, center_y - corner_y)


class CShapedArrow(Container):

    def __init__(
        self, start_x, start_y, end_x, end_y, offset, color, thickness, tip_height, round_radius=8
    ):
        # We will create an arrow that will look like this:
        #
        #    (start) ------|   [cor1]
        #                  |
        #                  |
        #                  |
        #  (end) <---------|   [cor2]
        #
        # Note that start and end points may have different x coordinates. Offset is measured from sp.x
        # For simplicity, the corners will be named as seen in the diagram in [cor1, cor2]
        #
        # Finally, bear in mind that (end) point may be above or below (start)
        #

        super().__init__(Point(start_x, start_y))
        self.round_radius = round_radius
        self.offset = offset
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        self.end_is_below = start_y < end_y

        cor1x, cor1y = start_x + offset, start_y
        cor2x, cor2y = cor1x, end_y

        if self.round_radius > 0:
            quad1, quad2 = 3, 1
            if not self.end_is_below:
                quad1, quad2 = 1, 3
            self.arc1 = RoundChamfer(cor1x, cor1y, quad1, self.round_radius, color, thickness)
            self.arc2 = RoundChamfer(cor2x, cor2y, quad2, self.round_radius, color, thickness)
            dhx_1, dvy_1 = self.arc1.delta_to_crossed_lines()
            dhx_2, dvy_2 = self.arc2.delta_to_crossed_lines()
            self.add(self.arc1)
            self.add(self.arc2)
        else:
            dhx_1, dvy_1 = 0, 0
            dhx_2, dvy_2 = 0, 0
            self.arc1 = None
            self.arc2 = None

        self.top_line = Line(start_x, start_y, cor1x + dhx_1, cor1y, color, thickness)
        self.vertical_line = Line(cor1x, cor1y + dvy_1, cor2x, cor2y + dvy_2, color, thickness)
        self.arrow = Arrow(cor2x + dhx_2, cor2y, end_x, end_y, color, thickness, tip_height)

        self.add(self.top_line)
        self.add(self.vertical_line)
        self.add(self.arrow)

    @property
    def end(self):
        # Given that we want to allow to overlap with other objects,
        # we will consider the arrow bounding box as a single point
        return self.position

    # remember that y-coordinates increase going down
    def c_height(self):
        return self.end_y - self.start_y

    def c_conflicts_with(self, other):
        # compares two CShapedArrows, and returns True if they overlap

        a_from, a_to = sorted([self.start_y, self.end_y])
        if isinstance(other, CShapedArrow):
            b_from, b_to = sorted([other.start_y, other.end_y])
        else:
            b_from, b_to = sorted(other)

        if a_to < b_from or a_from > b_to:
            return False
        else:
            return True


class NullArrow(Container):
    # We will create an arrow that will look like this:
    #
    #    (x,y) -|
    #           v
    #
    def __init__(self, x, y, length, tip_height, color, thickness):
        self.color = color
        self.thickness = thickness
        position = Point(x, y)
        elbow = Point(x + length, y)
        end = Point(x + length, y + length)
        self.line = Line(x, y, elbow.x, elbow.y, color, thickness)
        self.arrow = Arrow(elbow.x, elbow.y, end.x, end.y, color, thickness, tip_height)
        super().__init__(position)
        self.add(self.line)
        self.add(self.arrow)


class DeadArrow(Container):
    # We will create an arrow that will look like this:
    #
    #    (x,y) ->
    #
    def __init__(self, x, y, length, tip_height, color, thickness):
        self.color = color
        self.thickness = thickness
        position = Point(x, y)
        end = Point(x + length, y)
        self.line = Line(x, y, end.x, end.y, color, thickness)
        self.arrow = Arrow(position.x, position.y, end.x, end.y, color, thickness, tip_height)
        super().__init__(position)
        self.add(self.line)
        self.add(self.arrow)


class HeapToHeapArrowManager:

    def __init__(self, offset_step=15):
        self.base = 10
        self.offset_step = offset_step
        self.heap_arrows = []

    def clear(self):
        # This action does not remove the arrows from the scene
        # But instead, makes manager forget about them
        self.heap_arrows = []

    def add_arrow(self, sx, sy, ex, ey, color, thickness, tip_height):
        new_offset = self.base + self.offset_step
        # check previously existing arrows
        for parrow in sorted(self.heap_arrows, key=lambda a: (a.offset, a.c_height())):
            if parrow.offset == new_offset and parrow.c_conflicts_with((sy, ey)):
                new_offset = parrow.offset + self.offset_step
        darken_color = self.arrow_color(color, new_offset)
        new_arrow = CShapedArrow(sx, sy, ex, ey, new_offset, darken_color, thickness, tip_height)
        self.heap_arrows.append(new_arrow)
        return new_arrow

    def remove_arrow_if_heap_to_heap(self, arrow):
        if arrow in self.heap_arrows:
            self.heap_arrows.remove(arrow)

    def arrow_color(self, base_color, final_offset):
        # depending on offset, base_color is darkened
        colors = configs.POINTER_HEAP_ARROW_COLORS
        steps = int((final_offset - self.base) / self.offset_step) - 1
        if steps >= len(colors):
            steps = len(colors) - 1
        return colors[steps]
