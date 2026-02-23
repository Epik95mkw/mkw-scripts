from dolphin import gui # type: ignore

NO_DELAY = True

WHITE = 0xFFFFFFFF
BLUE = 0xFF00FFFF
YELLOW = 0xFFFFFF00
RED = 0xFFFF0000
ORANGE = 0xFFFFC000
GREEN = 0xFF00FF00
GRAY = 0xFF999999
LIGHTGRAY = 0xFFCCCCCC
T_WHITE = 0x88FFFFFF
T_BLACK = 0x50000000
T_RED = 0x88FF0000
T_GREEN = 0x8800FF00

def em(x):
    """convert em (font size units) to pixels"""
    return x * gui.get_font_size()

def vw(x):
    """convert vw (percent of viewport width) to pixels"""
    return x * gui.get_display_size()[0]

def vh(x):
    """convert vh (percent of viewport height) to pixels"""
    return x * gui.get_display_size()[1]