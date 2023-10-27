#https://stackoverflow.com/questions/281133/how-to-control-the-mouse-in-mac-using-python
from pathlib import Path
from typing import Tuple, Dict

# requirements files
from pynput.mouse import Button, Controller
import mss
from quickmachotkey import quickHotKey, mask
from quickmachotkey.configurators.jsonfile import JSONFileConfigurator
from quickmachotkey.constants import kVK_ANSI_X, cmdKey, controlKey, optionKey, kVK_ANSI_K
# RUNNING THE APP CONSTANTLY
from AppKit import NSApplication
from PyObjCTools import AppHelper


def click_monitor(monitor_number: int) -> None:
    mouse = Controller()    
    mouse.position = get_monitor_midpoint(monitor_number)
    mouse.click(Button.left, 1)

# https://github.com/moses-palmer/pynput/issues/350
# get the parameters of the displays
def get_monitor_midpoint(monitor) -> Tuple[int, int]:
    with mss.mss() as sct:
        monitor_values: Dict[str, int] = sct.monitors[monitor]

    horizontal_mid: int = monitor_values['left'] + int(monitor_values['width'] / 2)
    veritcal_mid: int = monitor_values['top'] + int(monitor_values['height'] / 2)
    print(horizontal_mid, veritcal_mid)
    return horizontal_mid, veritcal_mid

def main():
    with mss.mss() as sct:
        number_monitors: int = len(sct.monitors)

    # TODO creating various functions to handle input?
    for _ in range(1, number_monitors): # monitor value 0 = all in one version
        pass


    click_monitor(5)
    ''' # getting all five monitors and clicking to the position needed
    # center Monitor
    mouse.position = (412, 532)
    # Right Monitor
    mouse.position = (1829, -841)
    # Right Upper Monitor
    mouse.position = (1500, -2342)
    # Left Upper Monitor
    mouse.position = (-1500, -2342)
    # Left Monitor
    mouse.position = (-1829, -841)
    '''

# TODO -- how to make an initial version of keys that will be updated with what the user wants
# TODO -- wrap this in a class so that can call and create the new version of them item for the specific monitor?
# https://stackoverflow.com/a/75869640/7451892
config = JSONFileConfigurator(Path("whatkey.json")) # for updating the value of the virtualkey
@quickHotKey(virtualKey=kVK_ANSI_X, modifierMask=mask(cmdKey, controlKey, optionKey), configurator=config)
def application() -> None:
    print("handled ⌘⌃⌥X")
    print("handled, switching to K")
    application.configure(virtualKey=kVK_ANSI_K, modifierMask=mask(cmdKey, controlKey, optionKey))


if __name__ == '__main__':
    main()
    '''
    print("type ⌘⌃⌥X with any application focused")
    NSApplication.sharedApplication()
    AppHelper.runEventLoop()
    '''

''' TODO LIST
- add detector to add multiple monitor configurators
- how to have configurator using same file --> but with different values
- adding menu bar icon + spots to insert values for configurator
'''