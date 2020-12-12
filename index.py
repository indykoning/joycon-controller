#!/usr/bin/python3
import asyncio

import Configuration
from input import KeyboardControl, GamepadControl, ReplayControl
from SwitchController import SwitchController

configuration = Configuration.get()
loop = asyncio.get_event_loop()


def main():
    switch_controller = SwitchController()
    loop.run_until_complete(switch_controller.create(configuration))
    loop.run_until_complete(switch_controller.load_nfc())
    KeyboardControl.init_keyboard(switch_controller, configuration)
    GamepadControl.init_gamepad(switch_controller, configuration)
    ReplayControl.init_replay(switch_controller)

main()
# Configuration.save(configuration)
loop.run_forever()
