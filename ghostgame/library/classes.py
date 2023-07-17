import warnings
from time import time
from random import randint
import os

from .constants import NUM_DIMS


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
        panic_threshold (float): How long the ghost should be on the screen before using panic movement.
        time_last_panic_checked (float): Keeps track of the time (since epoch) that the panic last increased.
    """

    def __init__(self, max_health: float, passive_move_delay: float, panicked_move_delay: float):
        """
        Args:
            max_health (float): The initial health that the ghost should have.
            passive_move_delay (float): The time in seconds between each movement.
            panicked_move_delay (float) The time in seconds between each movement when panicking.
        """

        # Generate random location and dimension
        # self.angle = [0, 90]  # For debugging
        self.angle = [randint(0, 360), randint(0, 180)]
        self.current_dim = randint(1, NUM_DIMS)

        # Initialise health
        self.max_health = max_health
        self.health = max_health

        # Initialise move delay
        self.passive_move_delay = passive_move_delay
        self.panicked_move_delay = panicked_move_delay
        self.time_last_moved = time()

        # Initialise appearance
        self.appearance = [[[255, 255, 255]]]
        self.centre = [0, 0]

        # Initialise panic
        self.panic_progress = 0
        self.panic_threshold = 1
        self.time_last_panic_checked = time()

        warnNYI("Using the base class for Ghost types.")

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
        warnNYI("movePassively")

    def movePanicked(self):
        """ Performs a single movement when panicking (i.e., on screen or attacked). """
        #self.changeAngle(5, 0)
        warnNYI("movePanicked")

    def updatePanic(self, pxl_pos):
        """ Updates the panic_progress attribute, depending on whether the ghost is visible on the matrix or not.

        Args:
            pxl_pos: List containing [horizontal pixel position, vertical pixel position].
        """
        time_since_panic_checked = time() - self.time_last_panic_checked

        # If the ghost is on the matrix, increment the panic_progress attribute by time on matrix
        if 0 <= pxl_pos[0] <= 7 and 0 <= pxl_pos[1] <= 7:
            # Increase panic progress ad infinitum by the time it is on screen;
            # panic increases the longer the ghost is onscreen
            self.panic_progress += time_since_panic_checked
        # If the ghost is not on screen, and panic progress is not 0 yet, decrease it over time
        elif self.panic_progress > 0:
            self.panic_progress -= time_since_panic_checked
        # Panic progress is either negative or 0; lock to 0.
        else:
            self.panic_progress = 0

        # Update the time last checked, to keep track of the passage of time.
        self.time_last_panic_checked = time()

    def updateGhost(self, pxl_pos):
        """ Makes the ghost move depending on the arguments passed, and time since the ghost last moved

        Args:
            pxl_pos: List containing [horizontal pixel position, vertical pixel position].
        """
        # Update panic
        self.updatePanic(pxl_pos)

        # Perform movement; check panic progress to determine which function to run, then check if time to move
        # Passive movement
        if self.panic_progress < self.panic_threshold and self.getTimeSinceMoved() > self.passive_move_delay:
            self.movePassively()
            self.time_last_moved = time()
        # Panicked movement
        elif self.panic_progress >= self.panic_threshold and self.getTimeSinceMoved() > self.panicked_move_delay:
            self.movePanicked()
            self.time_last_moved = time()


# Used in ShutdownChecker
def checkEvent(event_, action, direction):
    return event_.action == action and event_.direction == direction


class ShutdownChecker:
    """ Keeps track of events passed into it, checking if right is pressed a number of times, then down, triggering
    a shutdown in case the Raspberry Pi cannot be shut down properly.

    Attributes:
        seq (list): Keeps track of joystick inputs passed into the checker object.
        num_clicks (int): How many times the right joystick must be pressed to make shut down possible.
        debug (bool): If True, will not actually shut down, and will instead stop the program.
    """

    def __init__(self, num_clicks=10, debug=False):
        self.seq = []
        self.num_clicks = num_clicks
        self.debug = debug

    def update(self, new_seq):
        # Add new events to the shutdown recording list
        self.seq += new_seq
        # Check for middle joystick clicked, resetting the list
        for event in new_seq:
            if event.action == "released" and event.direction == "middle":
                self.seq.clear()

        # Check for a sufficient number of events
        if len(self.seq) >= self.num_clicks * 2 + 2:

            # Count number of times right joystick was released
            count = 0
            for i in range(len(self.seq)):
                # The released events will be at odd indexes, so only need to check these events
                if i % 2 != 0:
                    if checkEvent(self.seq[i], "released", "right"):
                        count += 1
                    # If down is released as the last event in the list, shutdown
                    if count == self.num_clicks and checkEvent(self.seq[i], "released", "down"):
                        print("Shutdown")
                        if not self.debug:
                            os.system("sudo shutdown now")
                        else:
                            exit()

            # Clear list, so that this doesn't loop constantly
            self.seq.clear()
