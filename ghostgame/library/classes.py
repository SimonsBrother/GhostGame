from time import time


class Ghost:
    """ Stores data and behaviour for a ghost. A class for other types of ghost to inherit from.

    Attributes:
        angle (tuple): The horizontal and vertical angles from starting point at indexes 0 and 1 respectively.
            Initially (0, 0)
        current_dim (int): The dimension the ghost is currently at, initially 0.
        max_health (float): The maximum and initial amount of health a ghost has.
        health (float): The current amount of health a ghost has.
        move_delay (float): The time in seconds between each movement.
        panic_delay (float) The time in seconds between each movement when panicking.
        move_delay_base (float): The time to compare with, to determine when to move the ghost.
        animation_progress (dict): A dictionary for use by methods to keep track of progress of animations
        appearance: A 2D array [y][x] that stores tuples of 3 values (RGB) to represent the appearance of the ghost on
            the LED matrix.
    """

    def __init__(self, max_health: float, move_delay: float, panic_delay: float):
        """
        Args:
            max_health (float): The initial health that the ghost should have.
            move_delay (float): The time in seconds between each movement.
            panic_delay (float) The time in seconds between each movement when panicking.
        """

        self.angle = (0, 0)
        self.current_dim = 0

        self.max_health = max_health
        self.health = max_health

        self.move_delay = move_delay
        self.panic_delay = panic_delay
        self.move_delay_base = time()

        self.animation_progress = dict
        self.appearance = [[(255, 255, 255)]]

    def damaged(self, damage):
        """ Determines the behaviour of the ghost when it takes damage, and decreases current health.

        Args:
            damage: How much damage is inflicted.
        """
        ...

    def move(self):
        """ The behaviour of the ghost when not panicking (i.e., off screen). """
        ...

    def panic(self):
        """ The behaviour of the ghost when panicking (i.e., on screen and attacked). """
        ...
