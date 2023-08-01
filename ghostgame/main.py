import os

from library.classes import Ghost, GameManager
from library.constants import GameState

gm = GameManager()
# Initialise ghosts
ghosts = [Ghost()]

# Game loop
while True:
    gm.attack_system.attempting_attack = False

    # Get inputs from joystick
    new_events = gm.getNewJoystickEvents()
    gm.interpretNewEvents(new_events)

    # Continue playing game
    if gm.game_state == GameState.PLAY:
        # Make list of blank RGB values for rendering ghost images
        matrix = [(0, 0, 0) * 64]
        # Update ghosts
        sense_orientation = gm.sense_ref.orientation_degrees
        for ghost in ghosts:
            ghost.updateGhost(sense_orientation)

        # Update proximity bar
        gm.proximity_bar.update(ghosts)

        # Update LED matrix
        # Note that the ghost is not shown in this version
        gm.sense_ref.sense_hat.clear()
        gm.attack_system.renderHud(gm.sense_ref.sense_hat)  # Render attack system HUD first because it overwrites entire display
        gm.proximity_bar.render(gm.sense_ref.sense_hat)  # Proximity bar

    # Paused
    elif gm.game_state == GameState.PAUSED:
        print("Paused")

    # Info
    elif gm.game_state == GameState.INFO:
        print("Info")

    # Shut down Pi if shutdown sequence input
    if gm.shutdown_checker.update(new_events):
        os.system("sudo shutdown now")
