from skitso.shapes import Text

from tomos.ui.movie import configs


def build_text(text, **kwargs):
    font_name = kwargs.pop("font_name", "Monospace")
    font_size = kwargs.pop("font_size", configs.BASE_FONT_SIZE * configs.SCALE)
    x = kwargs.pop("x", 0)
    y = kwargs.pop("y", 0)
    return Text(x, y, text, font_name, font_size, **kwargs)
