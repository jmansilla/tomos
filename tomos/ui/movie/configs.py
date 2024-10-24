from manim import NORMAL
SCALE = 0.8

# TEXTs
BASE_FONT_SIZE = 12
TEXT_WEIGHT = NORMAL

# Variable Boxes
VAR_BOX_MIN_CHAR_RATIO = (0.85, 0.3)
VAR_MAX_CHARS_MIN_BOX = 7  # How many chars fit in the min box
VAR_BOX_EXTRA_CHAR_RATIO = (0.15, 0)  # to be added to box_min_char_ratio per extra char

COLOR_BY_TYPE = {
    "IntType": "#A2D2DF",
    "BoolType": "#F6EFBD",
    "RealType": "#E4C087",
    "CharType": "#BC7C7C",
    "PointerOf": "#0FEFBD",
    "ArrayOf": "#F4D345",
    }

UNNAMED_COLORS = ["red", "blue", "orange", "purple", "white"]
