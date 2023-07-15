from enum import Enum


class GhostState(Enum):
    PASSIVE = "passive"
    PANICKED = "panicked"


NUM_DIMS = 3

RANGE = 20  # The max range (in degrees) that ghosts can be observed on the LED matrix relative facing it directly
