from random import randint

from library.sensehat import calcPxlPos, calcImageData

from sense_hat import SenseHat


sense = SenseHat()
sense.clear()

target = (150, 90)
# target = (randint(0, 360), randint(0, 360))

# ap = [[(255, 255, 255)]]
blank = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
ap = [[red, green, red],
      [blank, white, green],
      [red, blue, red]]

centre = (1, 1)

while True:
    orient = sense.get_orientation_degrees()

    pxl_pos = calcPxlPos(sense, target)
    image_data = calcImageData(pxl_pos, ap, centre)

    sense.clear()
    for pixel_data in image_data:
        sense.set_pixel(*pixel_data)
