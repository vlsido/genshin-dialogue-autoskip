from random import randrange, uniform
from threading import Thread
from typing import Tuple, Union
from time import sleep, time
import vgamepad as vg

import pyautogui
from pynput.mouse import Controller
from pynput.keyboard import Key, KeyCode, Listener

# Dimensions of bottom dialogue option.
BOTTOM_DIALOGUE_MIN_X: int = 1300
BOTTOM_DIALOGUE_MAX_X: int = 1700
BOTTOM_DIALOGUE_MIN_Y: int = 790
BOTTOM_DIALOGUE_MAX_Y: int = 800

# Pixel coordinates for white part of the autoplay button.
KBM_AUTOPLAY_ICON_X: int = 111
KBM_AUTOPLAY_ICON_Y: int = 46

# Pixel coordinates for pink pixel of the autoplay button (DualShock 4 square). eng
DS4_ENG_AUTOPLAY_ICON_X: int = 1450
DS4_ENG_AUTOPLAY_ICON_Y: int = 1010

# Pixel coordinates for blue pixel of the confirm button (DualShock 4 cross). eng
DS4_ENG_CONFIRM_ICON_X: int = 1683
DS4_ENG_CONFIRM_ICON_Y: int = 1013

# Pixel coordinates for pink pixel of the autoplay button (DualShock 4 square). rus
DS4_RUS_AUTOPLAY_ICON_X: int = 1432
DS4_RUS_AUTOPLAY_ICON_Y: int = 1010

# Pixel coordinates for blue pixel of the confirm button (DualShock 4 cross). rus
DS4_RUS_CONFIRM_ICON_X: int = 1628
DS4_RUS_CONFIRM_ICON_Y: int = 1013

# Pixel coordinates for white part of the speech bubble in bottom dialogue option.
KBM_DIALOGUE_ICON_X: int = 1301
KBM_DIALOGUE_ICON_Y: int = 808

# Pixel coordinates for white part of the speech bubble in bottom dialogue option. (DualShock 4)
DS4_DIALOGUE_ICON_X: int = 1300
DS4_DIALOGUE_ICON_Y: int = 770

# Pixel coordinates near middle of the screen known to be white while the game is loading.
LOADING_SCREEN_X: int = 1200
LOADING_SCREEN_Y: int = 700


def define_ui() -> str:
    """
    Check autoplay and confirm (square and cross) buttons pixels for DS4 UI, and autoplay icon pixel for keyboard and
    mouse UI. Works for 1920x1080 game resolution.
    :return: String value that defines UI
    """
    ui = ""

    if get_pixel(1450, 1010) == (204, 114, 238) and get_pixel(1683, 1013) == (56, 161, 229):
        ui = "DS4_ENG"
    elif get_pixel(1432, 1010) == (204, 114, 238) and get_pixel(1628, 1013) == (56, 161, 229):
        ui = "DS4_RUS"
    elif get_pixel(KBM_AUTOPLAY_ICON_X, KBM_AUTOPLAY_ICON_Y) == (236, 229, 216):
        ui = "KBM"

    return ui


def get_pixel(x: int, y: int) -> Tuple[int, int, int]:
    """
    Return the RGB value of a pixel.
    :param x: The x coordinate of the pixel.
    :param y: The y coordinate of the pixel.
    :return: The RGB value of the pixel.
    """

    return pyautogui.pixel(x, y)


def random_interval() -> float:
    """
    Return a random interval between 0.12 and 0.18 seconds, or 0.18 and 0.3 seconds if a 6 is rolled.
    :return: A random interval between 0.12 and 0.18 seconds, or 0.18 and 0.3 seconds if a 6 is rolled.
    """

    return uniform(0.18, 0.3) if randrange(1, 7) == 6 else uniform(0.12, 0.18)


def random_cursor_position() -> Tuple[int, int]:
    """
    The cursor is moved to a random position in the bottom dialogue option.
    :return: A random (x, y) in range of the bottom dialogue option.
    """

    x: int = randrange(BOTTOM_DIALOGUE_MIN_X, BOTTOM_DIALOGUE_MAX_X + 1)
    y: int = randrange(BOTTOM_DIALOGUE_MIN_Y, BOTTOM_DIALOGUE_MAX_Y + 1)

    return x, y


def exit_program() -> None:
    """
    Listen for keyboard input to start, stop, or exit the program.
    :return: None
    """

    def on_press(key: (Union[Key, KeyCode, None])) -> None:
        """
        Start, stop, or exit the program based on the key pressed.
        :param key: The key pressed.
        :return: None
        """

        key_pressed: str = str(key)

        if key_pressed == 'Key.f8':
            main.status = 'run'
            print('RUNNING')
        elif key_pressed == 'Key.f9':
            main.status = 'pause'
            print('PAUSED')
        elif key_pressed == 'Key.f12':
            main.status = 'exit'
            exit()

    with Listener(on_press=on_press) as listener:
        listener.join()


def is_dialogue() -> bool:
    """
    Check if dialogue icon is present or not
    :return: Boolean True if dialogue icon is present, otherwise False
    """
    if get_pixel(DS4_DIALOGUE_ICON_X, DS4_DIALOGUE_ICON_Y) == (255, 255, 255) \
            and get_pixel(LOADING_SCREEN_X, LOADING_SCREEN_Y) != (255, 255, 255):
        return True

    if get_pixel(KBM_DIALOGUE_ICON_X, KBM_DIALOGUE_ICON_Y) == (255, 255, 255) \
            and get_pixel(LOADING_SCREEN_X, LOADING_SCREEN_Y) != (255, 255, 255):
        return True

    return False


def select_last_dialogue_option(ds4_gamepad: vg.VDS4Gamepad()) -> None:
    """
    Press 'up' on the gamepad to select the bottom dialogue option
    :param ds4_gamepad: Virtual DualShock 4 gamepad
    :return: None
    """
    ds4_gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH)
    ds4_gamepad.update()
    sleep(random_interval())
    ds4_gamepad.reset()
    ds4_gamepad.update()
    sleep(random_interval())


def press_cross(ds4_gamepad: vg.VDS4Gamepad()) -> None:
    """
    Press 'cross' on the gamepad
    :param ds4_gamepad: Virtual DualShock 4 gamepad
    :return: None
    """
    ds4_gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    ds4_gamepad.update()
    sleep(random_interval())
    ds4_gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    ds4_gamepad.update()
    sleep(random_interval())


def main() -> None:

    """
    Skip Genshin Impact dialogue when it's present based on the colors of some specific pixels.
    :return: None
    """

    main.status = 'pause'
    last_reposition: float = 0.0
    time_between_repositions: float = random_interval() * 40
    ds4_gamepad = vg.VDS4Gamepad()

    print('-------------\n'
          'F8 to start\n'
          'F9 to stop\n'
          'F12 to quit\n'
          '-------------')

    while True:
        while main.status == 'pause':
            sleep(0.5)

        if main.status == 'exit':
            print('Main program closing')
            break

        if define_ui() == "DS4_ENG" or is_dialogue():
            if is_dialogue():
                select_last_dialogue_option(ds4_gamepad)
            press_cross(ds4_gamepad)

        if define_ui() == "DS4_RUS" or is_dialogue():
            if is_dialogue():
                select_last_dialogue_option(ds4_gamepad)
            press_cross(ds4_gamepad)

        if define_ui() == "KBM" or is_dialogue():
            if time() - last_reposition > time_between_repositions:
                last_reposition = time()
                time_between_repositions = random_interval() * 40
                mouse.position = random_cursor_position()

            pyautogui.click()


if __name__ == "__main__":
    mouse = Controller()
    Thread(target=main).start()
    Thread(target=exit_program).start()
