from .constants import RANGE


def calcXAngularDisp(ghost_angle: float, sense_angle: float):
    """ Calculates the angular displacement between two values on a horizontal axis

    Args:
        ghost_angle: Horizontal angle of ghost from facing forwards (0 to 360 degrees)
        sense_angle: Horizontal angle of Sense HAT from facing forwards (0 to 360 degrees)

    Returns: The displacement between the two angles; negative values indicate ghost is left relative to Pi orientation,
    positive indicate ghost is right relative to Pi. A float value between -180 and 180 inclusive.
    """

    difference = ghost_angle - sense_angle

    # If out of range, normalise to be within -180 and 180
    if abs(difference) > 180:
        # If difference is negative
        if difference < 0:
            difference = 360 + difference
        # Else difference is positive
        else:
            difference = 360 - difference

    return difference


def calcYAngularDisp(ghost_angle: float, sense_angle: float):
    """ Calculates the angular displacement between two values on a vertical axis

    Args:
        ghost_angle: Vertical angle of ghost from facing downwards (0 to 180 degrees)
        sense_angle: Vertical angle of Sense HAT from facing downwards (0 to 360 degrees; will be limited)

    Returns: The displacement between the two angles; negative values indicate ghost is down relative to Pi orientation,
    positive indicate ghost is up relative to Pi. A float value between -180 and 180 inclusive.
    """
    # Limit out of range values
    if 180 < sense_angle <= 270:
        limited_sense_angle = 180
    elif 270 < sense_angle <= 360:
        limited_sense_angle = 0
    # Sense HAT vertically oriented between 0 and 180 inclusive
    else:
        limited_sense_angle = sense_angle

    difference = ghost_angle - limited_sense_angle

    return difference


def calcDist(x: float, y: float):
    """ Calculates the distance given an x and y component

    Args:
        x: x component of displacement
        y: y component of displacement

    Returns: The magnitude of displacement
    """

    return ((x ** 2) + (y ** 2)) ** 0.5


def calcPxlPos(angle_diffs):
    """ Determines the position on the sense HAT matrix the centre of the ghost should appear; does not limit to
    sense HAT matrix dimensions.

    Args:
        angle_diffs: List containing the [horizontal angular difference between target and point, same for vertical].

    Returns: a tuple containing (horizontal coordinate, vertical coordinate); may take values beyond sense HAT matrix
    """

    # Calculate pixel positions: each axis position is linearly related to the angle difference on that axis.
    """ Derivation
    y = mx + c
    When x = 0, y = 4, but y = c; so c = 3
    
    y = mx + 3
    When x = L, y = 7  (that is, when difference = limit, pixel should be at edge)
    so 7 = mL + 3
    
    mL = 4
    
    m = 4/L
    
    Y = 4x/L + 3
    """
    # Y value has to be inverted for some reason
    pxl_x = round(4 * angle_diffs[0]/RANGE + 3)
    pxl_y = round(4 * -angle_diffs[1]/RANGE + 3)

    return pxl_x, pxl_y


def calcImageData(core_pos: tuple, appearance: list, centre: tuple):
    """ Renders the ghost's appearance on the sense HAT LED matrix, relative to the ghost's core

    Args:
        core_pos: The position of the core on the matrix, a tuple
            containing (x coordinate of core on matrix, y coordinate of core on matrix).
        appearance: How the ghost should appear on the matrix; a 2D array containing
            tuples of RGB values (3 integers between 0 and 255 inclusive).
        centre: Index of the core of the ghost on the appearance array.

    Returns:
        A lost of tuples containing (x coordinate on matrix, y coordinate on matrix, pixel to display)
    """
    # Get the x and y coordinates of core on matrix
    core_x_m = core_pos[0]
    core_y_m = core_pos[1]

    pixels_to_show = []

    # For each row of pixels in appearance...
    for i, row in enumerate(appearance):
        # For each pixel in each row...
        for j, pxl in enumerate(row):
            # Calculate position of pixel relative to core pixel
            relative_x = core_x_m + (j - centre[0])
            relative_y = core_y_m + (i - centre[1])
            # Check that pixel fits on matrix
            if 0 <= relative_x <= 7 and 0 <= relative_y <= 7:
                pixels_to_show.append((relative_x, relative_y, pxl))

    return pixels_to_show
