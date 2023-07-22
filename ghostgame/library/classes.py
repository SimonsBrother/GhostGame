import os
import warnings
from random import randint
from time import time

from .constants import NUM_DIMS, RGB, RANGE
from .sensehat import calcXAngularDisp, calcYAngularDisp, calcDist, calcPxlPos


class NotImplementedWarning(Warning):
    pass


# Simple function to denote when something that should not be used is being used (e.g., the base class Ghost).
def warnNYI(msg=""):
    warnings.warn(msg, NotImplementedWarning)


class Ghost:
    """ Stores data and behaviour for a ghost. A class for other types of ghost to inherit from.

    Attributes:
        angle (list): The horizontal and vertical angles from starting point at indexes 0 and 1 respectively.
            Initially (0, 0)
        current_dim (int): The dimension the ghost is currently at, initially 0.
        max_health (float): The maximum and initial amount of health a ghost has.
        health (float): The current amount of health a ghost has.
        passive_move_delay (float): The time in seconds between each movement.
        panicked_move_delay (float) The time in seconds between each movement when panicking.
        time_last_moved (float): The time (since epoch) the ghost last moved at, used to determine when to move the ghost.
        appearance (list): A 2D array [y][x] that stores lists of 3 values (RGB) to represent the appearance of the ghost on
            the LED matrix.
        centre (list): The pixel within the appearance attribute that should be treated as the centre
        panic_progress (float): When this value equals the panic_threshold, the ghost panics.
        panic_threshold (float): How long the ghost should be on the screen before using panic movement.
        time_last_panic_checked (float): Keeps track of the time (since epoch) that the panic last increased.
    """

    def __init__(self, sense):
        """
        Args:
            sense: A SenseHAT object.
        """

        # Generate random location and dimension
        # self.angle = [0, 90]  # For debugging
        self.angle = [randint(0, 360), randint(0, 180)]
        self.current_dim = randint(1, NUM_DIMS)

        # Initialise health
        max_health = 10
        self.max_health = max_health
        self.health = max_health

        # Initialise move delay
        self.passive_move_delay = 1
        self.panicked_move_delay = 0.1
        self.time_last_moved = time()

        # Initialise appearance
        self.appearance = [[[255, 255, 255]]]
        self.centre = [0, 0]

        # Initialise panic
        self.panic_progress = 0
        self.panic_threshold = 1
        self.time_last_panic_checked = time()

        # Initialise data relating to Sense HAT
        self.sense_hat = sense
        sense_orientation = self.sense_hat.get_orientation_degrees()
        self.sense_x_disp = calcXAngularDisp(self.angle[0], sense_orientation['yaw'])
        self.sense_y_disp = calcYAngularDisp(self.angle[1], sense_orientation['roll'])
        self.sense_distance = calcDist(self.sense_x_disp, self.sense_y_disp)
        self.sense_pxl_pos = calcPxlPos(self.sense_x_disp, self.sense_y_disp)

        # Warn usage of base class
        if type(self) == Ghost:
            warnNYI("Using the base class for Ghost types.")

    def getTimeSinceMoved(self) -> float:
        """
        Returns:
            float: The time between now and when the ghost last moved
        """
        return time() - self.time_last_moved

    def damaged(self, damage: float):
        """ Determines the behaviour of the ghost when it takes damage, and decreases current health.

        Args:
            damage (float): How much damage is inflicted.
        """
        self.health -= damage
        # Make the ghost panic; note that the ghost will be on screen in order for damage to be applied
        self.panic_progress = self.panic_threshold

    def changeAngle(self, x: float, y: float) -> bool:
        """ Moves the ghost by x and y.

        Args:
            x (float): How much to change the horizontal angle by.
            y (float): How much to change the vertical angle by.

        Returns:
            bool: Whether the change to vertical angle was in range and applied.
        """
        # Apply horizontal movement
        self.angle[0] += x

        # Check if vertical movement can be applied, apply it is so
        in_range_after_moved = 0 <= self.angle[1] + y <= 180
        if in_range_after_moved:
            self.angle[1] += y

        return in_range_after_moved

    def movePassively(self):
        """ Performs a single movement when not panicking (i.e., off screen). """
        self.changeAngle(randint(-2, 2), randint(-2, 2))
        self.appearance[0][0] = [0, 255, 0]
        warnNYI("movePassively")

    def movePanicked(self):
        """ Performs a single movement when panicking (i.e., on screen or attacked). """
        self.changeAngle(randint(-5, 5), randint(-5, 5))
        self.appearance[0][0] = [255, 0, 0]
        warnNYI("movePanicked")

    def updatePanic(self, pxl_pos: list):
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

    def updateGhost(self):
        """ Updates ghost's panic/passive state, position, and data regarding position from sense HAT. """
        # Update panic
        self.sense_pxl_pos = calcPxlPos(self.sense_x_disp, self.sense_y_disp)
        self.updatePanic(self.sense_pxl_pos)

        # Perform movement; check panic progress to determine which function to run, then check if time to move
        # Passive movement
        if self.panic_progress < self.panic_threshold and self.getTimeSinceMoved() > self.passive_move_delay:
            self.movePassively()
            self.time_last_moved = time()
        # Panicked movement
        elif self.panic_progress >= self.panic_threshold and self.getTimeSinceMoved() > self.panicked_move_delay:
            self.movePanicked()
            self.time_last_moved = time()

        # Recalculate displacements and distance from sense HAT
        sense_orientation = self.sense_hat.get_orientation_degrees()
        self.sense_x_disp = calcXAngularDisp(self.angle[0], sense_orientation['yaw'])
        self.sense_y_disp = calcYAngularDisp(self.angle[1], sense_orientation['roll'])
        self.sense_distance = calcDist(self.sense_x_disp, self.sense_y_disp)

    def calcImageData(self) -> list:
        """ Renders the ghost's appearance on the sense HAT LED matrix, relative to the ghost's core

        Returns:
            list: A list of tuples containing (x coordinate on matrix, y coordinate on matrix, pixel to display)
        """
        # Get the x and y coordinates of core on matrix
        core_x_m = self.sense_pxl_pos[0]
        core_y_m = self.sense_pxl_pos[1]

        pixels_to_show = []

        # For each row of pixels in appearance...
        for i, row in enumerate(self.appearance):
            # For each pixel in each row...
            for j, pxl in enumerate(row):
                # Calculate position of pixel relative to core pixel
                relative_x = core_x_m + (j - self.centre[0])
                relative_y = core_y_m + (i - self.centre[1])
                # Check that pixel fits on matrix
                if 0 <= relative_x <= 7 and 0 <= relative_y <= 7:
                    pixels_to_show.append((relative_x, relative_y, pxl))

        return pixels_to_show

    def __repr__(self):
        return f"Ghost at {self.angle}, health: {self.health}/{self.max_health}, panic progress: {self.panic_progress};"


# Used in ShutdownChecker
def checkJoystickEvent(event_, action, direction):
    return event_.action == action and event_.direction == direction


class ShutdownChecker:
    """ Keeps track of events passed into it, checking if right is pressed a number of times, then down, triggering
    a shutdown in case the Raspberry Pi cannot be shut down properly.

    Attributes:
        stick_event_log (list): Keeps track of joystick inputs passed into the checker object.
        direction (str): The direction the joystick must be pressed multiple times before shut down is possible.
        num_clicks (int): How many times the right joystick must be pressed to make shut down possible.
        debug (bool): If True, will not actually shut down, and will instead stop the program.
    """

    def __init__(self, direction: str, num_clicks=10, debug=False):
        self.stick_event_log = []
        self.direction = direction
        self.num_clicks = num_clicks
        self.debug = debug

    def update(self, new_stick_log: list):
        # Add new events to the shutdown recording list
        self.stick_event_log += new_stick_log
        # Check for middle joystick clicked, resetting the list
        for event in new_stick_log:
            if event.action == "released" and event.direction == "middle":
                self.stick_event_log.clear()

        # Check for a sufficient number of events
        if len(self.stick_event_log) >= self.num_clicks * 2 + 2:

            # Count number of times joystick was released in the set direction
            count = 0
            for i in range(len(self.stick_event_log)):
                # The released events will be at odd indexes, so only need to check these events
                if i % 2 != 0:
                    if checkJoystickEvent(self.stick_event_log[i], "released", self.direction):
                        count += 1
                    # If down is released as the last event in the list, shutdown
                    if count == self.num_clicks and checkJoystickEvent(self.stick_event_log[i], "released", "down"):
                        print("Shutdown")
                        if not self.debug:
                            os.system("sudo shutdown now")
                        else:
                            exit()

            # Clear list, so that this doesn't loop constantly
            self.stick_event_log.clear()


class ProximityBar:
    """ Shows how close the nearest ghost is via a bar on the sense HAT matrix

    """

    def __init__(self, max_distance=150, colors=None):
        self.colors: list

        if colors is not None:
            self.colors = colors
        else:
            self.colors = [RGB.RED, RGB.ORANGE, RGB.ORANGE, RGB.YELLOW,
                           RGB.YELLOW, RGB.GREEN, RGB.GREEN, RGB.BLUE]

        self.max_distance = max_distance
        self.bar_height = -1

    def update(self, ghosts):
        """ Performs calculations needed to update the proximity bar"""
        # Determine which ghost data has the lowest data
        nearest_ghost = ghosts[0]  # Use first ghost as placeholder
        for ghost in ghosts:
            # Check if ghost is closer
            if ghost.sense_distance < nearest_ghost.sense_distance:
                # Update closest ghost data
                nearest_ghost = ghost

        """ Derivation of linear relationship between proximity bar height (x) and nearest ghost distance (y) 
        y = mx + c

        When x = D, y = 0, where D = max distance proximity bar should begin rendering
        0 = Dm + c
        c = -Dm
        
        When x = L√2 (L = limit), y = 7
        7 = mL√2 + c
        But c = -Dm, so 7 = mL√2 - Dm
        7 = m(L√2 - D)
        m = 7/(L√2 - D)
        
        y = mx + c
        But c = -Dm, so y = mx - Dm
        y = m(x - D)
        But m = 7/(L√2 - D), so y = 7(x - D)/(L√2 - D)
        
        y = 7(x - D)/(L√2 - D)
        Where y = proximity bar height from 0 to 7 inclusive, 
        x = distance from 150 to √2 of L (where L = LIMIT) inclusive, respectively.
        """
        bar_height = round((7 * (nearest_ghost.sense_distance - self.max_distance)) / ((2 ** 0.5) * RANGE - self.max_distance))
        # Limit bar height
        if bar_height > 7:
            bar_height = 7

        self.bar_height = bar_height
        return self.bar_height

    def render(self, sense):
        # If ghost within proximity range
        if 0 <= self.bar_height <= 7:
            # Determine color to use
            color = self.colors[7 - self.bar_height].value
            # Render bar
            for i in range(7, 7 - self.bar_height - 1, -1):
                sense.set_pixel(0, i, color)
