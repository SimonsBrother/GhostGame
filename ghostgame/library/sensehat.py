from .constants import RANGE


def calcXAngularDisp(ghost_angle: float, sense_angle: float) -> float:
    """ Calculates the angular displacement between two values on a horizontal axis

    Args:
        ghost_angle: Horizontal angle of ghost from facing forwards (0 to 360 degrees)
        sense_angle: Horizontal angle of Sense HAT from facing forwards (0 to 360 degrees)

    Returns:
        float: The displacement between the two angles; negative values indicate ghost is left relative to Pi orientation,
    positive indicate ghost is right relative to Pi. May return -180 to 180 inclusive.
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


def calcYAngularDisp(ghost_angle: float, sense_angle: float) -> float:
    """ Calculates the angular displacement between two values on a vertical axis

    Args:
        ghost_angle: Vertical angle of ghost from facing downwards (0 to 180 degrees)
        sense_angle: Vertical angle of Sense HAT from facing downwards (0 to 360 degrees; will be limited)

    Returns:
        float: The displacement between the two angles; negative values indicate ghost is down relative to Pi orientation,
    positive indicate ghost is up relative to Pi. May return -180 to 180 inclusive.
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


def calcDist(x_disp: float, y_disp: float) -> float:
    """ Calculates the distance given an x and y component

    Args:
        x_disp (float): Horizontal component of displacement.
        y_disp (float): Vertical component of displacement.

    Returns:
        float: The magnitude of displacement.
    """

    return ((x_disp ** 2) + (y_disp ** 2)) ** 0.5


def calcPxlPos(x_disp: float, y_disp: float) -> list:
    """ Determines the position on the sense HAT matrix the centre of the ghost should appear; does not limit to
    sense HAT matrix dimensions.

    Args:
        x_disp (float): Horizontal component of displacement.
        y_disp (float): Vertical component of displacement.

    Returns:
        list: a tuple containing (horizontal coordinate, vertical coordinate); may take values beyond sense HAT matrix
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
    pxl_x = round(4 * x_disp / RANGE + 3)
    pxl_y = round(4 * -y_disp / RANGE + 3)

    return [pxl_x, pxl_y]
