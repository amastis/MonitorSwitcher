#https://stackoverflow.com/questions/281133/how-to-control-the-mouse-in-mac-using-python
import os
from pathlib import Path
import json
from typing import Tuple, Dict, Callable

# requirements files
from pynput.mouse import Button, Controller
import mss
from quickmachotkey import quickHotKey, mask
from quickmachotkey.configurators.jsonfile import JSONFileConfigurator
from quickmachotkey.constants import cmdKey, controlKey, optionKey, kVK_ANSI_X, kVK_ANSI_C, kVK_ANSI_B, kVK_ANSI_K, kVK_ANSI_L

# RUNNING THE APP CONSTANTLY
from AppKit import NSApplication
from PyObjCTools import AppHelper


class MonitorSwitcher(object):
    """handling the creation of shortcuts for monitors to move the cursor from monitor to monitor"""
    def __init__(self):
        self.monitor_command_file: str = 'commands.json'


    def _first_run_check(self) -> bool:
        return self.monitor_command_file in os.listdir()


    def _convert_key_to_virtualKey(self, key) -> int:
        # because the keys are stored in self.monitor_command_file as the actual command values instead of the key values -- need a func to convert from the command values to key values
        key_codes: Dict[str, int] = {
            'A': int(0x0),
            'B': int(0xB),
            'C': int(0x8),
            'D': int(0x2),
            'E': int(0xE),
            'F': int(0x3),
            'G': int(0x5),
            'H': int(0x4),
            'I': int(0x22),
            'J': int(0x26),
            'K': int(0x28),
            'L': int(0x25),
            'M': int(0x2E),
            'N': int(0x2D),
            'O': int(0x1F),
            'P': int(0x23),
            'Q': int(0xC),
            'R': int(0xF),
            'S': int(0x1),
            'T': int(0x11),
            'U': int(0x20),
            'V': int(0x9),
            'W': int(0xD),
            'X': int(0x7),
            'Y': int(0x10),
            'Z': int(0x6),
        }
        return key_codes.get(key)


    def _get_command_file(self) -> Dict[str, Dict[str, int]]:
        with open(self.monitor_command_file, 'r') as file:
            monitor_commands = json.load(file)
        return monitor_commands


    def create_monitors(self) -> None:
        if not self._first_run_check():
            return # TODO get user input on what commands should be for each monitor

        monitor_commands = self._get_command_file()

        # TODO -- if user changes values -- how is this impacted? / How to destroy current versions and recreate new ones in their place...
        for item in monitor_commands.keys():
            print(item)
            #item = u'{item}' # TODO CHECK if this works otherwise...
            self._create_monitor(item[-1]) # TODO currently only the final key is what is changing


    def _get_monitor_index(self, command_used: str) -> int:
        # TODO how to setup this monitors.json file on initial run through...
        monitor_values = self._get_command_file()[command_used]

        # from all monitors find the correct monitor based on location (may change during use)
        with mss.mss() as sct:
            for index, item in enumerate(sct.monitors[1:]):
                if monitor_values['left'] == item['left'] and monitor_values['top'] == item['top']:
                    return index + 1


    # https://github.com/moses-palmer/pynput/issues/350
    # get the parameters of the displays
    def _get_monitor_midpoint(self, monitor: int) -> Tuple[int, int]:
        with mss.mss() as sct:
            monitor_values: Dict[str, int] = sct.monitors[monitor]

        horizontal_mid: int = monitor_values['left'] + int(monitor_values['width'] / 2)
        veritcal_mid: int = monitor_values['top'] + int(monitor_values['height'] / 2)

        return horizontal_mid, veritcal_mid


    def _click_monitor(self, monitor_number: int) -> None:
        mouse = Controller()
        mouse.position = self._get_monitor_midpoint(monitor_number)
        mouse.click(Button.left, 1)


    # create a monitor based on the command files stored
    def _create_monitor(self, key) -> Callable:
        print(key)
        key_code = self._convert_key_to_virtualKey(key) # TODO currently only the final key is what is changing
        @quickHotKey(virtualKey=key_code, modifierMask=mask(cmdKey, optionKey))
        def monitor() -> None:
            print(f"handled ⌘⌥{key}")
            self._click_monitor(self._get_monitor_index(f"⌘⌃⌥{key}"))

        return monitor


'''
# https://stackoverflow.com/a/75869640/7451892
config = JSONFileConfigurator(Path("whatkey.json")) # for updating the value of the virtualkey
@quickHotKey(virtualKey=kVK_ANSI_X, modifierMask=mask(cmdKey, controlKey, optionKey), configurator=config)
def application() -> None:
    print("handled ⌘⌃⌥X")
    print("handled, switching to K")
    application.configure(virtualKey=kVK_ANSI_K, modifierMask=mask(cmdKey, controlKey, optionKey))
'''


def main():
    monitor_obj = MonitorSwitcher()
    monitor_obj.create_monitors()

    #NSApplication.sharedApplication()
    #AppHelper.runEventLoop()


if __name__ == '__main__':
    main()

''' TODO LIST
- add detector to add multiple monitor configurators
- how to have configurator using same file --> but with different values
- adding menu bar icon + spots to insert values for configurator
'''