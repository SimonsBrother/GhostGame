from sense_hat import SenseHat
import math

sense = SenseHat()
sense.clear()


def calcAngleDist(p, s):
    difference = abs(s - p)
    if difference < 180:
        return difference
    else:
        return 360 - difference


while True:
    orient = sense.get_orientation_degrees()
    x = orient['yaw']
    y = orient['roll']

    x_diff = calcAngleDist(150, x)
    y_diff = calcAngleDist(90, y)
    # print(f"x: {round(calcAngleDist(150, x))}, y: {round(calcAngleDist(90, y))}")
    print(f"{round(pow(x_diff ** 2 + y_diff ** 2, 0.5))}")

    sense.clear()
    pxl_y = round(4 * (math.sin(math.radians(y_diff))) + 8)
    if 0 <= pxl_y <= 7:
        sense.set_pixel(0, pxl_y, 0, 255, 0)
