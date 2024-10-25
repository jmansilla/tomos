from manim import Text
from tomos.ui.movie import configs


def build_text(text, **kwargs):
    if "weight" not in kwargs:
        kwargs["weight"] = configs.TEXT_WEIGHT
    if not "font_size" in kwargs:
        kwargs["font_size"] = configs.BASE_FONT_SIZE * configs.SCALE
    if not "font" in kwargs:
        kwargs["font"] = "Monospace"

    return Text(text, **kwargs)
