from skitso.atom import Container, Point
from skitso.shapes import Arrow, Line

from tomos.ui.movie import configs
from tomos.ui.movie.texts import build_text


class CShapedArrow(Container):
    counter = [0]

    def __init__(self, start_x, start_y, end_x, end_y, offset, color, thickness, tip_height):
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
        super().__init__(Point(start_x, start_y))

        cnt = CShapedArrow.counter[0]
        CShapedArrow.counter[0] += 1

        cor1x, cor1y = start_x + offset * (cnt+1), start_y
        cor2x, cor2y = cor1x, end_y
        top_line = Line(start_x, start_y, cor1x, cor1y, color, thickness)
        vertical_line = Line(cor1x, cor1y, cor2x, cor2y, color, thickness)
        arrow = Arrow(cor2x, cor2y, end_x, end_y, color, thickness, tip_height)

        self.add(top_line)
        self.add(vertical_line)
        self.add(arrow)


class DeadArrow(Container):
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
