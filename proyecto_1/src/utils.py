from enum import Enum

# SYSTEM VARIABLES
NUM_CPU = 4
PROCESS_DELAY = 0.5
CYCLES_DELAY = 5

MEM_DELAY = 1.5
CACHE_RD_DELAY = MEM_DELAY * 0.40
CACHE_WR_DELAY = MEM_DELAY * 0.60


# COLOR PRINTS
RED = "31m"
GREEN = "32m"
YELLOW = "33m"
BLUE = "34m"
MAGENTA = "35m"
CIAN = "36m"
WHITE = "37m"

# GUI specs
GUIDE = 'whitesmoke'
FONT = "Century Gothic"
BORDER = "black"
WINDOW = "gainsboro"
MENU = "#d2d2d2"
EDGES = "#b0b0b0"
NOTE = "black"
BACKGROUND = "white"
FONTGROUND = "black"
ADDSECTION = MENU
# Animations
HIGHLIGHT_HIT = "limegreen"
HIGHLIGHT_READ = "gold"
HIGHLIGHT_WRITE = "turquoise"
HIGHLIGHT_RQ = "blueviolet"
HIGHLIGHT_INV = "crimson"
HIGHLIGHT_WB = "hotpink"

padding = 1
height = 28


# Enumeración de tipos de mensaje para el bus
class AccessType(Enum):
    readmiss = 0
    writemiss = 1
    calc = 2
