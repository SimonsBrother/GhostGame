import warnings
from time import time
from random import randint

from .constants import GhostState, NUM_DIMS


class NotImplementedWarning(Warning):
    pass


def warnNYI(msg=""):
    warnings.warn(msg, NotImplementedWarning)


class Ghost:
    """ Stores data and behaviour for a ghost. A class for other types of ghost to inherit from.

    Attributes:
        angle (tuple): The horizontal and vertical angles from starting point at indexes 0 and 1 respectively.
            Initially (0, 0)
        current_dim (int): The dimension the ghost is currently at, initially 0.
        max_health (float): The maximum and initial amount of health a ghost has.
        health (float): The current amount of health a ghost has.
        passive_move_delay (float): The time in seconds between each movement.
        panicked_move_delay (float) The time in seconds between each movement when panicking.
        time_last_moved (float): The time (since epoch) the ghost last moved at, used to determine when to move the ghost.
        appearance: A 2D array [y][x] that stores tuples of 3 values (RGB) to represent the appearance of the ghost on
            the LED matrix.
        centre (tuple): The pixel within the appearance attribute that should be treated as the centre
        panic_progress (float): When this value equals the panic_threshold, the ghost panics.
        panic_threshold (float): How long the ghost should be on the screen before panicking.
        time_last_panic_increased (float): Keeps track of the time (since epoch) that the panic last increased.
    """

    def __init__(self, max_health: float, passive_move_delay: float, panicked_move_delay: float):
        """
        Args:
            max_health (float): The initial health that the ghost should have.
            passive_move_delay (float): The time in seconds between each movement.
            panicked_move_delay (float) The time in seconds between each movement when panicking.
        """

        # Generate random location and dimension
        self.angle = (randint(0, 360), randint(0, 360))
        self.current_dim = randint(1, NUM_DIMS)

        # Initialise health
        self.max_health = max_health
        self.health = max_health

        # Initialise move delay
        self.passive_move_delay = passive_move_delay
        self.panicked_move_delay = panicked_move_delay
        self.time_last_moved = time()

        # Initialise appearance
        self.appearance = [[(255, 255, 255)]]
        self.centre = (0, 0)

        # Initialise panic
        self.panic_progress = 0
        self.panic_threshold = 1
        self.time_last_panic_increased = time()

    def getTimeSinceMoved(self) -> float:
        """
        Returns:
            float: The time between now and when the ghost last moved
        """
        return time() - self.time_last_moved

    def damaged(self, damage):
        """ Determines the behaviour of the ghost when it takes damage, and decreases current health.

        Args:
            damage: How much damage is inflicted.
        """
        self.health -= damage
        # Make the ghost panic; note that the ghost will be on screen in order for damage to be applied
        self.panic_progress = self.panic_threshold

    def changeAngle(self, x, y):
        """ Moves the ghost by x and y.

        Args:
            x: How much to change the horizontal angle by.
            y: How much to change the vertical angle by.
        """
        self.angle[0] += x
        self.angle[1] += y

    def movePassively(self):
        """ Performs a single movement when not panicking (i.e., off screen). """
        self.changeAngle(0, randint(-2, 2))
        warnNYI("movePassively")  # todo

    def movePanicked(self):
        """ Performs a single movement when panicking (i.e., on screen or attacked). """
        self.changeAngle(5, 0)
        warnNYI("movePanicked")  # todo

    def updatePanic(self):
        ...
        # If the ghost is on the matrix, increment the panic_progress attribute; otherwise, reset panic
        # if ghost on matrix
        #    self.panic_progress += time() - self.time_last_panic_increased
        #    self.time_last_panic_increased = time()
        # else:
        #    self.panic_progress = 0

    def updateGhost(self, sense):
        """ Makes the ghost move depending on the arguments passed, and time since the ghost last moved """
        ...

        # Perform movement; check panic progress to determine which function to run, then check if time to move
        # Passive movement
        if self.panic_progress < self.panic_threshold and self.getTimeSinceMoved() > self.passive_move_delay:
            self.movePassively()
            self.time_last_moved = time()
        # Panicked movement
        elif self.panic_progress >= self.panic_threshold and self.getTimeSinceMoved() > self.panicked_move_delay:
            self.movePanicked()
            self.time_last_moved = time()
