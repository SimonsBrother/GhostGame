from enum import Enum


class GhostState(Enum):
    PASSIVE = "passive"
    PANICKED = "panicked"


RANGE = 90  # The max range (in degrees) that ghosts can be observed on the LED matrix
SENSITIVITY = 3.5  # Affects how many pixels the ghost appears to move by when you move the sense HAT
