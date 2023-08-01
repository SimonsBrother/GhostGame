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
        list: A list containing (horizontal coordinate, vertical coordinate); may take values beyond sense HAT matrix.
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

# TODO: Test
def checkPxlDistFromEdge(pxl_pos: list, dist_from_edge: int) -> bool:
    """ Determines if the pixel position provided is a certain distance from the edge of the sense HAT matrix.

    Args:
        pxl_pos: The coordinates on the matrix to check.
        dist_from_edge: The distance from the edge of the sense HAT matrix.

    Returns:
        bool: Whether the ghost is at least the distance dist_from_edge from the edge of the sense HAT matrix.
    """
    return dist_from_edge <= pxl_pos[0] <= (7 - dist_from_edge) and dist_from_edge <= pxl_pos[1] <= (7 - dist_from_edge)

# TODO: Test
def getFocusEffect(bc: list, fc: list) -> list:
    """ Builds a list of colors to apply to the sense HAT matrix, forming a square on it.

    Args:
        bc (list): The background color, in the form [R, G, B].
        fc (list): The focus color, in the form [R, G, B].

    Returns:
        list: An array that can be passed to the sense HAT to apply the focus.
    """
    return [bc, bc, bc, bc, bc, bc, bc, bc,
            bc, fc, fc, fc, fc, fc, fc, bc,
            bc, fc, bc, bc, bc, bc, fc, bc,
            bc, fc, bc, bc, bc, bc, fc, bc,
            bc, fc, bc, bc, bc, bc, fc, bc,
            bc, fc, bc, bc, bc, bc, fc, bc,
            bc, fc, fc, fc, fc, fc, fc, bc,
            bc, bc, bc, bc, bc, bc, bc, bc]
