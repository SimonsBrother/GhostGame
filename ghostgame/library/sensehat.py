import math


from .constants import RANGE


def calcAngularDisp(p, s):
    """ Calculates the angular displacement between two values on a single axis

    Args:
        p: Angle of a certain point (0 to 360 degrees)
        s: Angle of another point (0 to 360 degrees)

    Returns: The displacement between the two angles; negative values indicate down or left,
    positive indicate up or right.

    """
    difference = abs(s - p)
    # I don't really know why this direction bit works; I messed about with it, and it seems to.
    direction = -1 if (p - s) > 0 else 1

    if difference < 180:
        return difference * direction
    else:
        return (360 - difference) * -direction


def calcDist(x: float, y: float):
    """ Calculates the distance given an x and y component

    Args:
        x: x component of displacement
        y: y component of displacement

    Returns: The magnitude of displacement
    """

    return pow(x ** 2 + y ** 2, 0.5)


def calcPxlPos(sense, target_angle: tuple):
    """ Determines the position on the sense HAT matrix the centre of the ghost should appear; does not limit to
    sense HAT matrix dimensions.

    Args:
        sense: A SenseHAT object.
        target_angle (tuple): The angles to compare the sense HAT orientation with, in
            format (horizontal angle, vertical angle).

    Returns: a tuple containing (horizontal coordinate, vertical coordinate); may take values beyond sense HAT matrix

    """
    orient = sense.get_orientation_degrees()
    x = orient['yaw']
    y = orient['roll']

    x_diff = calcAngularDisp(target_angle[0], x)
    y_diff = calcAngularDisp(target_angle[1], y)

    print(f"x: {round(x_diff)}, y: {round(y_diff)}")

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
    # X value has to be inverted for some reason
    pxl_x = round(4 * -x_diff/RANGE + 3)
    pxl_y = round(4 * y_diff/RANGE + 3)
    # print(pxl_x, pxl_y)

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
