from library.classes import Ghost, ShutdownChecker, ProximityBar

from sense_hat import SenseHat


sense = SenseHat()
sense.set_imu_config(False, True, False)
sense.clear()

ghost = Ghost(sense)

# Shutdown checker
shutdown_checker = ShutdownChecker("right", debug=True)

proximity_bar = ProximityBar()

# Main loop
while True:
    # Get inputs

    # Update ghosts
    ghost.updateGhost()

    proximity_bar.update([ghost])
    image_data = ghost.calcImageData()

    # Update matrix
    sense.clear()

    proximity_bar.render(sense)

    for pixel_data in image_data:
        sense.set_pixel(*pixel_data)

    # Shutdown check
    shutdown_checker.update(sense.stick.get_events())
