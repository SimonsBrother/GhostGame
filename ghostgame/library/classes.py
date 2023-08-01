import warnings
from random import randint
from time import time
from math import floor
from threading import Thread, Lock

from .constants import NUM_DIMS, RGB, RANGE, StickDir, StickAct, HUDState, GameState
from .sensehat import calcXAngularDisp, calcYAngularDisp, calcDist, calcPxlPos, getFocusEffect

from sense_hat import SenseHat, InputEvent


class NotImplementedWarning(Warning):
    pass


# Simple function to denote when something that should not be used is being used (e.g., the base class Ghost).
def warnNYI(msg=""):
    warnings.warn(msg, NotImplementedWarning)


class SenseHatRef:
    """ Stores a reference to the senseHAT and continually updates the orientation via a thread.

    Attributes:
        sense_hat (SenseHat): Stores a reference to the SenseHat object in use.
        orientation_degrees (dict): Stores the current roll, pitch, and yaw of the sense HAT.
        thread (Thread): Stores the thread that continually updates the orientation; started in constructor.
        lock (Lock): Stores the lock that controls access to orientation_degrees.
    """
    def __init__(self, sense_hat: SenseHat):
        self.sense_hat = sense_hat
        self.orientation_degrees = self.sense_hat.get_orientation_degrees()

        self.thread = Thread(target=self.repeatedlyUpdateOrientation)
        self.lock = Lock()

        self.thread.start()

    def repeatedlyUpdateOrientation(self):
        """ Updates the orientation attribute, until the sense_hat attribute is None. To be passed to thread. """
        # Only continue to loop if the SenseHat object is set.
        while self.sense_hat is not None:
            # Lock the orientation_degrees attribute, update it, and unlock it.
            with self.lock:
                self.orientation_degrees = self.sense_hat.get_orientation_degrees()


# TODO: test; implement dimension indicator on matrix
class GameManager:
    def __init__(self):
        self.sense_ref = SenseHatRef(SenseHat())
        self.sense_ref.sense_hat.set_imu_config(False, True, False)

        # Set initial game state to be in the main menu
        self.game_state = GameState.MENU

        # Dimensions
        self.current_dim = 1
        self.dim_colors = (RGB.RED, RGB.GREEN, RGB.BLUE)

        # Subsystems
        self.shutdown_checker = ShutdownChecker(StickDir.UP, debug=True)
        self.proximity_bar = ProximityBar()
        self.attack_system = AttackSystem()

    # TODO: test
    def resetSenseHAT(self):
        """ Resets the sense HAT by reassigning sense_ref to a new SenseHat object. """
        self.sense_ref.sense_hat = SenseHat()
        self.sense_ref.sense_hat.set_imu_config(False, True, False)

    def getNewJoystickEvents(self):
        """ Retrieves new events from joystick since last call (basically calls get_events). """
        return self.sense_ref.sense_hat.stick.get_events()

    def interpretNewEvents(self, events: [InputEvent]):
        """ Handles new events from the senseHAT joystick. """
        # Iterate over each event and perform
        for event in events:
            # Toggle info
            if checkJoystickEvent(event, StickDir.RIGHT):
                self.toggleInfo()
                return

            # Toggle pause
            elif checkJoystickEvent(event, StickDir.LEFT):
                self.togglePause()
                return

            # Increment dimension
            elif checkJoystickEvent(event, StickDir.UP):
                self.incrementDim()
                return

            # Decrement dimension
            elif checkJoystickEvent(event, StickDir.DOWN):
                self.decrementDim()
                return

            # Attempt to attack
            elif checkJoystickEvent(event, StickDir.MIDDLE):
                self.attemptAttack()
                return

    def toggleInfo(self):
        """ Set game state to pause if not paused, otherwise, set game state to play.
        This indicates if the game should be paused or not. """

        # If not showing info, show info
        if self.game_state != GameState.INFO:
            self.game_state = GameState.INFO
        # If showing info, switch back to game
        else:
            self.game_state = GameState.PLAY

    def togglePause(self):
        # If not paused, pause
        if self.game_state != GameState.PAUSED:
            self.game_state = GameState.PAUSED
        # If paused, unpause
        else:
            self.game_state = GameState.PLAY

    def incrementDim(self):
        if self.current_dim < NUM_DIMS:
            self.current_dim += 1

    def decrementDim(self):
        if self.current_dim > 1:
            self.current_dim -= 1

    def attemptAttack(self):
        self.attack_system.attempting_attack = True


class GhostRelativeSenseHAT:
    """ Stores data of the ghost relative to the sense HAT
    Attributes:
        ghost (Ghost): A reference to the ghost using this instance.
        x_disp (float): The horizontal displacement of a ghost relative to the sense HAT.
        y_disp (float): The vertical displacement of a ghost relative to the sense HAT.
        distance (float): The distance of a ghost relative to the sense HAT.
        pxl_pos (list): The displacement of the ghost from the centre of the sense HAT matrix in the form [horizontal
        displacement, vertical displacement].
    """
    def __init__(self, ghost):
        self.ghost = ghost
        self.x_disp = 0
        self.y_disp = 0
        self.distance = 0
        self.pxl_pos = []

    def updateDisplacements(self, sense_orientation: dict):
        """ Updates the displacements of the ghost relative to sense HAT. """
        print(sense_orientation['yaw'], sense_orientation['roll'])
        self.x_disp = calcXAngularDisp(self.ghost.angle[0], sense_orientation['yaw'])
        self.y_disp = calcYAngularDisp(self.ghost.angle[1], sense_orientation['roll'])

    def updateDistance(self):
        """ Updates the distance attribute, depending on the displacement attributes. """
        self.distance = calcDist(self.x_disp, self.y_disp)

    def updatePxlPos(self):
        """ Updates the pxl_pos attribute, depending on the displacement attributes. """
        self.pxl_pos = calcPxlPos(self.x_disp, self.y_disp)


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

    def __init__(self):
        # Generate random location and dimension
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

        # Initialise reference to Sense HAT, and its related data
        self.relative_sense = GhostRelativeSenseHAT(self)

        # Warn usage of base class
        if type(self) == Ghost:
            warnNYI("Using the base class for Ghost types.")

    def getTimeSinceMoved(self) -> float:
        """
        Returns:
            float: The time between now and when the ghost last moved
        """
        return time() - self.time_last_moved

    def damage(self, damage: float):
        """ Determines the behaviour of the ghost when it takes damage, and decreases current health.

        Args:
            damage (float): How much damage is inflicted.
        """
        self.health -= damage
        # Make the ghost panic; note that the ghost will be on screen in order for damage to be applied
        if self.panic_progress < self.panic_threshold:
            self.panic_progress = self.panic_threshold
        # TODO: ghost death

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

    def updateMovement(self):
        """ Perform movement; check panic progress to determine which function to run, then check if time to move. """
        # Passive movement
        if self.panic_progress < self.panic_threshold and self.getTimeSinceMoved() > self.passive_move_delay:
            self.movePassively()
            self.time_last_moved = time()
        # Panicked movement
        elif self.panic_progress >= self.panic_threshold and self.getTimeSinceMoved() > self.panicked_move_delay:
            self.movePanicked()
            self.time_last_moved = time()

    def updateRelativeSenseData(self, sense_orientation: dict):
        """ Recalculate displacements and distance from sense HAT. """
        self.relative_sense.updateDisplacements(sense_orientation)
        self.relative_sense.updateDistance()

    def updateGhost(self, sense_orientation: dict):
        """ Updates ghost's panic/passive state, position, and data regarding position from sense HAT. """
        # Update panic
        self.relative_sense.updatePxlPos()
        self.updatePanic(self.relative_sense.pxl_pos)

        # Update movement
        self.updateMovement()

        # Update data relative to sense HAT
        self.updateRelativeSenseData(sense_orientation)

    def calcImageData(self) -> list:
        """ Renders the ghost's appearance on the sense HAT LED matrix, relative to the ghost's core

        Returns:
            list: A list of tuples containing (x coordinate on matrix, y coordinate on matrix, pixel to display)
        """
        # Get the x and y coordinates of core on matrix
        core_pxl = self.relative_sense.pxl_pos
        core_pxl_x = core_pxl[0]
        core_pxl_y = core_pxl[1]

        pixels_to_show = []

        # For each row of pixels in appearance...
        for i, row in enumerate(self.appearance):
            # For each pixel in each row...
            for j, pxl in enumerate(row):
                # Calculate position of pixel relative to core pixel
                relative_x = core_pxl_x + (j - self.centre[0])
                relative_y = core_pxl_y + (i - self.centre[1])
                # Check that pixel fits on matrix
                if 0 <= relative_x <= 7 and 0 <= relative_y <= 7:
                    pixels_to_show.append((relative_x, relative_y, pxl))

        return pixels_to_show

    def __repr__(self):
        return f"Ghost at {self.angle}, health: {self.health}/{self.max_health}, " \
               f"panic progress: {self.panic_progress}/{self.panic_progress};"


# Used in ShutdownChecker
def checkJoystickEvent(event_, direction: StickDir, action=StickAct.RELEASED) -> bool:
    """ Returns true if some event has certain characteristics.

    Args:
        event_: The event to evaluate.
        action: The action to check for, either StickAct value PRESSED, RELEASED, or HELD.
        direction: The direction of the joystick to check for, either StickDir value UP, DOWN, LEFT, RIGHT, or MIDDLE.

    Returns:
        bool: Whether the event provided matches the action and direction provided.
    """
    # Validate action and direction
    if not (action in StickAct and direction in StickDir):
        raise ValueError("Invalid action or direction.")

    return event_.action == action.value and event_.direction == direction.value


class ShutdownChecker:
    """ Keeps track of events passed into it, checking if right is pressed a number of times, then down, triggering
    a shutdown in case the Raspberry Pi cannot be shut down properly.

    Attributes:
        stick_event_log (list): Keeps track of joystick inputs passed into the checker object.
        direction (str): The direction the joystick must be pressed multiple times before shut down is possible.
        num_clicks (int): How many times the right joystick must be pressed to make shut down possible.
        debug (bool): If True, will not actually shut down, and will instead stop the program.
    """

    def __init__(self, direction: StickDir, num_clicks=10, debug=False):
        """
        Args:
            direction: The direction the joystick must be pressed before the Pi can be shutdown.
            num_clicks: How many times the joystick must be pressed in 'direction' before the Pi can be shutdown.
            debug: If True, the program will only exit, instead of shutting down the Pi.
        """
        self.stick_event_log = []
        self.direction = direction
        self.num_clicks = num_clicks
        self.debug = debug

    def shutdown(self):
        ...

    def update(self, new_stick_log: list):
        """ Checks new events from joystick for shutdown sequence; if the shutdown sequence was input, return True. """
        # Add new events to the shutdown recording list
        self.stick_event_log += new_stick_log
        # Check for middle joystick clicked, resetting the list
        for event in new_stick_log:
            if checkJoystickEvent(event, StickDir.MIDDLE):
                self.stick_event_log.clear()

        # Check for a sufficient number of events
        if len(self.stick_event_log) >= self.num_clicks * 2 + 2:
            # Count number of times joystick was released in the set direction
            count = 0
            for i in range(len(self.stick_event_log)):  # TODO: for loop could be optimised
                # The released events will be at odd indexes, so only need to check these events
                if i % 2 != 0:
                    if checkJoystickEvent(self.stick_event_log[i], self.direction):
                        count += 1
                    # If the joystick has been pressed in the required direction the required number of times,
                    # followed by down, return True to signify shutdown.
                    return count == self.num_clicks and checkJoystickEvent(self.stick_event_log[i], StickDir.DOWN)  # TODO test this still works

            # Clear list, so that this doesn't loop constantly
            self.stick_event_log.clear()


class ProximityBar:
    """ Shows how close the nearest ghost is via a line on the sense HAT matrix.

    Attributes:
        colors (list): A list containing 8 lists of the form [R, G, B], that specifies the range of colors to use.
        max_distance (float): The maximum distance that ghosts can be detected from.
        bar_height (int): The height of the bar after the update method is called.
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

    def update(self, ghosts: [Ghost]):
        """ Performs calculations needed to update the proximity bar. """
        # Determine which ghost data has the lowest data
        nearest_ghost = ghosts[0]  # Use first ghost as placeholder
        for ghost in ghosts:
            # Check if ghost is closer
            if ghost.relative_sense.distance < nearest_ghost.relative_sense.distance:
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
        # TODO: Tweak RANGE use in equation? (to make bar only full when closer to ghost
        bar_height = round((7 * (nearest_ghost.relative_sense.distance - self.max_distance)) / ((2 ** 0.5) * RANGE - self.max_distance))
        # Limit bar height
        if bar_height > 7:
            bar_height = 7

        self.bar_height = bar_height
        return self.bar_height

    def render(self, sense_hat: SenseHat):
        """ Displays the proximity bar on the sense HAT. """
        # If ghost within proximity range
        if 0 <= self.bar_height <= 7:
            # Determine color to use
            color = self.colors[7 - self.bar_height].value
            # Render bar
            for i in range(7, 7 - self.bar_height - 1, -1):
                sense_hat.set_pixel(0, i, color)

# TODO test
class AttackSystem:
    """

    """
    def __init__(self):
        self.attack_cooldown = 3
        self.time_last_attacked = time()
        self.attempting_attack = False
        self.hud_state = HUDState.OFF

        self.charge_colors = [RGB.BLANK, RGB.RED, RGB.YELLOW, RGB.GREEN]

    def canAttack(self) -> bool:
        """ Checks if attack cooldown is complete, returns True if it is. """
        can_attack = (time() - self.time_last_attacked) > self.attack_cooldown
        self.time_last_attacked = time()
        return can_attack

    def renderHud(self, sense_hat: SenseHat):
        # Get time since last attacked
        charge_bar_height = floor(time() - self.time_last_attacked)
        # Limit to cooldown
        charge_bar_height = self.attack_cooldown if charge_bar_height >= self.attack_cooldown else charge_bar_height

        # Build focus HUD (an orange square of varying brightness)
        focus_effect = None
        if self.hud_state == HUDState.DIM:
            # Dim orange square
            focus_effect = getFocusEffect(RGB.BLANK.value, [133, 53, 0])
        elif self.hud_state == HUDState.BRIGHT:
            # Bright orange square
            focus_effect = getFocusEffect(RGB.BLANK.value, [184, 73, 0])

        # Render focus effect
        if focus_effect:
            sense_hat.set_pixels(focus_effect)

        # Render charge bar
        charge_bar_color = self.charge_colors[charge_bar_height].value
        for i in range(7, 7 - charge_bar_height, -1):
            sense_hat.set_pixel(7, i, charge_bar_color)
