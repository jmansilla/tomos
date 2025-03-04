from skitso.shapes import Text

from tomos.ui.movie import configs


class HighlightableText(Text):
    # Similar to skitso.shapes.Text, but with an is_highlighted attribute
    # Each time is drawn, if is_highlighted is True, there will be applied an outline
    # grabbed from configs.HIGHLIGHT_COLOR and configs.HIGHLIGHT_OUTLINE_WIDTH
    # Also, bear in mind that if configs.AUTO_DE_HIGHLIGHT is True, is_highlighted will be
    # set to False after each draw

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_highlighted = False

    def get_params(self):
        params = super().get_params()
        if self.is_highlighted:
            params["stroke_fill"] = configs.HIGHLIGHT_OUTLINE_COLOR
            params["stroke_width"] = configs.HIGHLIGHT_OUTLINE_WIDTH
            params["fill"] = configs.HIGHLIGHT_COLOR
        return params

    def draw_me(self, pencil):
        super().draw_me(pencil)
        if configs.AUTO_DE_HIGHLIGHT:
            self.is_highlighted = False


def build_text(text, **kwargs):
    if kwargs.pop("highlightable", False):
        klass = HighlightableText
    else:
        klass = Text
    font_name = kwargs.pop("font_name", "Monospace")
    font_size = kwargs.pop("font_size", configs.BASE_FONT_SIZE * configs.SCALE)
    x = kwargs.pop("x", 0)
    y = kwargs.pop("y", 0)

    return klass(x, y, text, font_name, font_size, **kwargs)
