print('shall include here some import from ENV that allows to override these configs')

CANVAS_SIZE = (1280, 720)
CANVAS_COLOR = "#1A1A1D"

MEMORY_BOARD_SIZE = (300, CANVAS_SIZE[1] * 0.9) # we'll have one for stack and one for heap
PADDING = 12

SCALE = 1

# TEXTs
BASE_FONT_SIZE = 20
# TEXT_WEIGHT = NORMAL

# Variable Boxes
VAR_BOX_MIN_CHAR_RATIO = (80, 30)

COLOR_BY_TYPE = {
    "IntType": "#13005A",
    "BoolType": "#00337C",
    "RealType": "#1C82AD",
    "CharType": "#005B41",
    "PointerOf": "#289e84",
    "ArrayOf": "#F4D345",
    }

ARRAY_ORIENTATION = "vertical"  # "vertical" or "horizontal". Default: "vertical"

UNNAMED_COLORS = ["red", "blue", "orange", "purple", "black", "pink"]

CODEBOX_BGCOLOR = "#000000"
CODEBOX_NEXT_LINE_BGCOLOR = "#4d0000"
CODEBOX_PREV_LINE_BGCOLOR = "#004d00"