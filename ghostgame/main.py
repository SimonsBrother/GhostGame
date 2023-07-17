from library.sensehat import calcPxlPos, calcImageData, calcDist, calcXAngularDisp, calcYAngularDisp
from library.classes import Ghost, ShutdownChecker

from sense_hat import SenseHat


sense = SenseHat()
sense.clear()

ghost = Ghost(10, 1, 0.5)

# Shutdown checker
shutdown_checker = ShutdownChecker(debug=True)

# Main loop
while True:
    orient_deg = sense.get_orientation_degrees()

    x = orient_deg['yaw']
    y = orient_deg['roll']

    x_diff = calcXAngularDisp(ghost.angle[0], x)
    y_diff = calcYAngularDisp(ghost.angle[1], y)
    print("diff:", round(x_diff), round(y_diff))

    angle_diffs = [x_diff, y_diff]

    pxl_pos = calcPxlPos(angle_diffs)
    ghost.updateGhost(pxl_pos)
    image_data = calcImageData(pxl_pos, ghost.appearance, ghost.centre)

    # Sensor bar
    distance = calcDist(x_diff, y_diff)
    print("Distance:", distance)
    dist_pxl = round((7 / 254.5) * distance)

    sense.clear()

    # Sensor bar
    if 0 <= dist_pxl <= 7:
        for i in range(dist_pxl):
            sense.set_pixel(0, i, 0, 100, 0)

    for pixel_data in image_data:
        sense.set_pixel(*pixel_data)

    shutdown_checker.update(sense.stick.get_events())
