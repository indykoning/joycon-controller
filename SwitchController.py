import asyncio
import glob
import logging
import os
import sys

sys.path.insert(0, "./joycontrol")
from joycontrol.controller import Controller
from joycontrol.controller_state import button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
from joycontrol import logging_default as log


class SwitchController:
    async def create(self, configuration={}):
        """Initialize connection to the switch"""
        log.configure(logging.INFO)
        print("Connecting...")
        self.spi_flash = FlashMemory()
        self.controller = Controller.PRO_CONTROLLER

        self.factory = controller_protocol_factory(
            self.controller, spi_flash=self.spi_flash
        )
        self.transport, self.protocol = await create_hid_server(
            self.factory, reconnect_bt_addr=configuration.get("reconnect_bt_addr")
        )
        self.controller_state = self.protocol.get_controller_state()
        print("Connected!")

    def is_valid_button(self, *buttons):
        """Check if the button press is available on the controller"""
        for button in buttons:
            if button not in self.controller_state.button_state.get_available_buttons():
                return False
        return True

    async def hold(self, *buttons):
        """Hold given buttons down"""
        if self.is_valid_button(*buttons) is False:
            return

        # Make sure controller is connected
        await self.controller_state.connect()
        await button_press(self.controller_state, *buttons)

    async def release(self, *buttons):
        """Release given buttons"""
        if self.is_valid_button(*buttons) is False:
            return

        # Make sure controller is connected
        await self.controller_state.connect()
        await button_release(self.controller_state, *buttons)

    async def stick(self, side, direction=None, release=False):
        """Handle stick direction, remembering previous pressed. Allowing left+up etc."""
        if direction in ("left", "right"):
            if release:
                await self.stick_h_pct(side)
            else:
                await self.stick_h_pct(side, direction == "right")
        if direction in ("up", "down"):
            if release:
                await self.stick_v_pct(side)
            else:
                await self.stick_v_pct(side, direction == "up")

    async def map_pct_to_stick(self, pct, center, left, right):
        """Convert percentage to stick position"""
        return int((center - left) + (pct * (left + right)))

    async def stick_h_pct(self, side, pct=0.5):
        """Convert percentage value to horizontal switch input"""
        stick = (
            self.controller_state.r_stick_state
            if side == "right"
            else self.controller_state.l_stick_state
        )
        calibration = stick.get_calibration()
        pos = await self.map_pct_to_stick(pct, calibration.h_center, calibration.h_max_below_center, calibration.h_max_above_center)
        stick.set_h(pos)

    async def stick_v_pct(self, side, pct=0.5):
        """Convert percentage value to vertical switch input"""
        stick = (
            self.controller_state.r_stick_state
            if side == "right"
            else self.controller_state.l_stick_state
        )
        calibration = stick.get_calibration()
        pos = await self.map_pct_to_stick(pct, calibration.v_center, calibration.v_max_below_center, calibration.v_max_above_center)
        stick.set_v(pos)

    async def nfc(self, file_path):
        """Load nfc file from file path"""
        with open(file_path, "rb") as nfc_file:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, nfc_file.read)
            self.controller_state.set_nfc(content)

    async def load_nfc(self):
        """Load first nfc file in nfc folder"""
        for file in glob.glob("nfc/*.bin"):
            filepath = os.path.join(os.getcwd(), file)
            await self.nfc(filepath)
            print("Loaded in nfc from %s" % filepath)
            break
