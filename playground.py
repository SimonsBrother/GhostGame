from ghostgame.library.sensehat import calcXAngularDisp, calcYAngularDisp

from sense_hat import SenseHat

sense = SenseHat()
sense.set_imu_config(False, True, False)

target = (0, 90)

while True:
    orient_deg = sense.get_orientation_degrees()

    x = orient_deg['yaw']
    y = orient_deg['roll']
    z = orient_deg['pitch']

    x_diff = calcXAngularDisp(target[0], x)
    y_diff = calcYAngularDisp(target[1], y)

    #print("raw:", round(x - z), round(y - z))
    print("diff:", round(x_diff), round(y_diff), "raw:", round(x), round(y), round(z))
