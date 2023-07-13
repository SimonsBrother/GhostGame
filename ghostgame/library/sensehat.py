import math


from .constants import RANGE, SENSITIVITY


def calcAngularDisp(p, s):
    """ Calculates the angular displacement between two values

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
    orient = sense.get_orientation_degrees()
    x = orient['yaw']
    y = orient['roll']

    x_diff = calcAngularDisp(target_angle[0], x)
    y_diff = calcAngularDisp(target_angle[1], y)

    print(f"x: {round(x_diff)}, y: {round(y_diff)}")

    # Calculate pixel positions: convert to radians, apply sine (invert for x-axis),
    pxl_x = round((-(math.sin(math.radians(x_diff))) + 1) * SENSITIVITY)
    pxl_y = round(((math.sin(math.radians(y_diff)) + 1) * SENSITIVITY))


    # Check that angle is in range and that pixel coordinates are valid
    if (-RANGE <= x_diff <= RANGE and -RANGE <= y_diff <= RANGE) and (0 <= pxl_x <= 7 and 0 <= pxl_y <= 7):
        return pxl_x, pxl_y
    else:
        return None
