from io import BytesIO
from PIL import Image

from skitso.atom import BaseImgElem, Container, Point

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments_ayed2.style import Ayed2Style

from tomos.ui.movie.texts import build_text


class CodeBox(BaseImgElem):
    line_pad = 2
    def __init__(self, source_code, language="ayed2", font_size=18, bg_color="#000000"):
        self.source_code = source_code
        self.language = language
        self.font_size = font_size
        self.bg_color = bg_color
        self.lexer = get_lexer_by_name(language)
        self.formatter = self.get_formatter()
        self.background = None

    def highlight(self, code):
        return Image.open(BytesIO(highlight(code, self.lexer, self.formatter)))

    def get_formatter(self):
        style = Ayed2Style
        style.background_color = self.bg_color
        return ImageFormatter(
            font_size=self.font_size,
            line_pad=self.line_pad,
            line_numbers=True,
            style=style,
        )

    def draw_me(self, pencil):
        img = self.highlight(self.source_code)
        x, y = self.position
        pencil.image.paste(img, (x, y))


class TomosCode(Container):

    def __init__(self, source_code, language="ayed2"):
        position = Point(0, 0)
        super().__init__(position)
        self.language = language
        self.source_code = source_code
        self.code_img = CodeBox(source_code, language=language)
        self.code_img.position = position
        self.add(self.code_img)
        self.focuser = self.build_focuser()

    def build_focuser(self):
        pass

    def focus_line(self, line_number):
        pass

    def build_hint(self, msg):
        pass


