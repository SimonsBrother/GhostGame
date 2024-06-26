from library.classes import Ghost, GameManager
from library.constants import GameState

gm = GameManager()

# Initialise ghosts
gm.ghosts = [Ghost()]

# Game loop
while True:
    gm.attack_system.attempting_attack = False

    # Get inputs from joystick
    new_events = gm.getNewJoystickEvents()
    gm.interpretNewEvents(new_events)

    # Continue playing game
    if gm.game_state == GameState.PLAY:
        # Make list of blank RGB values for rendering ghost images

        # Update ghosts
        sense_orientation = gm.sense_ref.orientation_degrees
        for ghost in gm.ghosts:
            ghost.updateGhost(sense_orientation)

        # todo process attacking

        # Update proximity bar
        gm.proximity_bar.update(gm.ghosts)

        # Update LED matrix
        gm.render()

    # Paused
    elif gm.game_state == GameState.PAUSED:
        print("Paused")

    # Info
    elif gm.game_state == GameState.INFO:
        print("Info")

    # Shut down Pi if shutdown sequence input
    if gm.shutdown_checker.update(new_events):
        print("shut down signal")
        # os.system("sudo shutdown now")
