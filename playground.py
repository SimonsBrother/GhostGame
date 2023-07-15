red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
ap = [[red, green, red],
      [blue, white, green],
      [red, blue, red]]
ap.reverse()
centre = (1, 1)

x = 3
y = 3

for i, row in enumerate(ap):
    for j, pxl in enumerate(row):
        x_r = x + (i - centre[0])
        y_r = y + (j - centre[1])
        if 0 <= x_r <= 7 and 0 <= y_r <= 7:
            print(x_r, y_r, pxl)
