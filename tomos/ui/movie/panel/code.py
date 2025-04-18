from logging import getLogger
from io import BytesIO
from PIL import Image

from skitso.atom import BaseImgElem, Container, Point

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments_ayed2.style import Ayed2Style

from tomos.ui.movie import configs


logger = getLogger(__name__)


class NextPrevLineFormatter(ImageFormatter):
    _NEXT = "next"
    _PREV = "prev"

    def __init__(self, *args, next_line_nr=None, prev_line_nr=None, **kwargs):
        color_order = []
        if next_line_nr is None:
            if prev_line_nr is None:
                # should not happen, unless we are in the
                # section of types/vars definitions
                lines = []
            else:
                lines = [prev_line_nr]
                color_order = [self._PREV]
        else:
            if prev_line_nr is None:
                lines = [next_line_nr]
                color_order = [self._NEXT]
            else:
                lines = sorted([prev_line_nr, next_line_nr])
                if next_line_nr < prev_line_nr:
                    color_order = [self._NEXT, self._PREV]
                else:
                    color_order = [self._PREV, self._NEXT]
        kwargs["hl_lines"] = lines
        super().__init__(*args, **kwargs)
        self.color_order = color_order
        self._hl_next_color = configs.CODEBOX_NEXT_LINE_BGCOLOR
        self._hl_prev_color = configs.CODEBOX_PREV_LINE_BGCOLOR

    @property
    def hl_color(self):
        # this attribute will be consumed in ascending order (by line number)
        if not self.color_order:
            return self._hl_color
        which = self.color_order.pop(0)
        if which == self._PREV:
            return self._hl_prev_color
        else:
            return self._hl_next_color

    @hl_color.setter
    def hl_color(self, color):
        self._hl_color = color


class CodeBox(BaseImgElem):
    line_pad = 2

    def __init__(self, source_code, language="ayed2", font_size=18, bg_color=None):
        self.source_code = source_code
        self.language = language
        self.font_size = font_size
        self.bg_color = bg_color or configs.CODEBOX_BGCOLOR
        self.lexer = get_lexer_by_name(language)
        self.background = None
        self.next_line_nr = None
        self.prev_line_nr = None

    def highlight(self, code):
        return Image.open(BytesIO(highlight(code, self.lexer, self.formatter)))

    def update_next_line_nr(self, line_nr):
        self.prev_line_nr = self.next_line_nr
        self.next_line_nr = line_nr

    @property
    def formatter(self):
        kw = {
            "font_size": self.font_size,
            "line_pad": self.line_pad,
            "line_numbers": True,
            "next_line_nr": self.next_line_nr,
            "prev_line_nr": self.prev_line_nr,
        }
        if configs.CODEBOX_STYLE in ["ayed2", "ayed"]:
            style = Ayed2Style
            style.background_color = self.bg_color
            kw["style"] = style
        return NextPrevLineFormatter(**kw)

    def draw_me(self, pencil):
        img = self.highlight(self.source_code)
        x, y = self.position
        pencil.image.paste(img, (round(x), round(y)))

    @property
    def end(self):
        if not hasattr(self, "position"):
            raise ValueError("Position not set")
        if not hasattr(self, "relative_end"):
            pass
        tmp_img = self.highlight(self.source_code)
        self.relative_end = Point(tmp_img.size[0], tmp_img.size[1])
        return self.position + self.relative_end


class TomosCode(Container):

    def __init__(self, source_code, language="ayed2"):
        position = Point(0, 0)
        super().__init__(position)
        self.language = language
        self.source_code = source_code
        self.code_generator = CodeBox(source_code, language=language)
        self.code_generator.position = position
        self.add(self.code_generator)

    def mark_next_line(self, line_number):
        self.code_generator.update_next_line_nr(line_number)

    def build_hint(self, msg):
        pass
