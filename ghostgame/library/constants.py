from enum import Enum


class RGB(Enum):
    RED = [255, 0, 0]
    GREEN = [0, 255, 0]
    BLUE = [0, 0, 255]
    BLANK = [0, 0, 0]
    WHITE = [255, 255, 255]
    ORANGE = [252, 107, 3]
    YELLOW = [252, 248, 3]
    CYAN = [3, 252, 207]
    PURPLE = [123, 3, 252]
    PINK = [252, 3, 232]


# The number of explorable dimensions to have in the game
NUM_DIMS = 3

RANGE = 20  # The max range (in degrees) that ghosts can be observed on the LED matrix relative facing it directly
