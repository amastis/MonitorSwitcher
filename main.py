import os
import json
from typing import Callable, List, Dict, Any

import rumps
import mss
# LOCAL FILES
import commands
import generate_image


def _open_json(file_name: str) -> Dict[str, Any]:
    with open(file_name, 'r') as file:
        return json.load(file)

def _save_json(file_name: str, new_dict: Dict[str, Any]) -> None:
    with open(file_name, 'w') as file:
        json.dump(new_dict, file)

def _get_monitor_values(monitor_num: str) -> Dict[str, int]:
    with mss.mss() as sct:
        return sct.monitors[int(monitor_num)]

def save_monitor_command(monitor_num: int, command: str) -> None:
    original_commands: Dict[str, Any] = {}
    commands_update: Dict[str, Any] = {}
    if 'monitorKey.json' in os.listdir():
        # check if there is an original command to replace
        original_commands = _open_json('monitorKey.json')
        if original_commands.get(monitor_num): # update monitor commands + commands json lookups
            original_command: str = original_commands[monitor_num]
            commands_update = _open_json('commands.json')
            del commands_update[original_command]

    # update the values in the dicts to save to json
    original_commands[monitor_num] = command
    commands_update[command] = _get_monitor_values(monitor_num)

    _save_json('commands.json', commands_update)
    _save_json('monitorKey.json', original_commands)

class MonitorSwitcher(rumps.App):
    def __init__(self):
        self.app = rumps.App("Monitor Switcher") # TODO update icon
        self.monitor_image_name: str = generate_image.main()
        print(self.monitor_image_name)
        with mss.mss() as sct:
            self.monitors_num: int = len(sct.monitors) - 1

        if self.monitors_num == 0:
            print('please connect to a monitor')

        self.app.menu = self.monitors_layout_image()
        self.create_monitor_inputs()
        commands.main()


    '''
    @rumps.timer(10)
    def check_monitors() -> bool:
        with mss.mss() as sct:
            monitors_num: int = len(sct.monitors) - 1

        return self.monitors_num != monitors_num
    '''

    def monitors_layout_image(self) -> List[rumps.MenuItem]:
        art_menu = []
        art_path = self.monitor_image_name
        if art_path and os.path.isfile(art_path):
            art_menu = [rumps.MenuItem("", callback=None, icon=art_path, dimensions=[192, 192]), None]

        return art_menu


    def _monitor_prefs(self, monitor_num: int) -> Callable:
        @rumps.clicked(f'Monitor: {monitor_num}')
        def prefs(self):
            label: str = f'Monitor: {monitor_num}'
            response = rumps.Window(message='Insert Command for Monitor Hot Key', title=f"{label} Hot Key", default_text='defaulted', ok='Save').run()
            save_monitor_command(monitor_num, response.text)
            print(label, response.text)
        return prefs

    # create correct number of functions to get input for monitors
    def create_monitor_inputs(self) -> None:
        for i in range(self.monitors_num):
            self._monitor_prefs(i + 1)
    

    def run(self):
        self.app.run()


if __name__ == "__main__":
    MonitorSwitcher().run()
