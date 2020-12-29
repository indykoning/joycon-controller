#!/usr/bin/python3
import asyncio

import Configuration
from input import KeyboardControl, GamepadControl, ReplayControl
from SwitchController import SwitchController
from watchgod import awatch


configuration = Configuration.get()
loop = asyncio.get_event_loop()

async def watch_nfc_folder(switch_controller):
    async for changes in awatch('nfc/'):
        await switch_controller.load_nfc()

def main():
    switch_controller = SwitchController()
    loop.run_until_complete(switch_controller.create(configuration))
    loop.run_until_complete(switch_controller.load_nfc())
    KeyboardControl.init_keyboard(switch_controller, configuration)
    GamepadControl.init_gamepad(switch_controller, configuration)
    ReplayControl.init_replay(switch_controller)
    loop.create_task(watch_nfc_folder(switch_controller))

main()
# Configuration.save(configuration)
loop.run_forever()
