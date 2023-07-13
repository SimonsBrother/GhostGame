from library.sensehat import calcPxlPos

from sense_hat import SenseHat

sense = SenseHat()
sense.clear()

while True:
    orient = sense.get_orientation_degrees()

    sense.clear()
    pxl_pos = calcPxlPos(sense, (150, 90))

    if pxl_pos:
        sense.set_pixel(*pxl_pos, 0, 255, 0)
