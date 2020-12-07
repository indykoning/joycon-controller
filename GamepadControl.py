from inputs import get_gamepad
import asyncio


def init_gamepad(switch_controller, configuration={}):
    """initialize everything for gamepad support"""
    button_last_state = {}

    async def listen():
        """Loop forever to listen to gamepad events"""
        while True:
            await process_gamepad()

    async def process_gamepad():
        """Wait for gamepad event and handle them"""
        events = await asyncio.get_event_loop().run_in_executor(None, get_gamepad)
        for event in events:
            mapped_button = configuration.get("button_mapping", {}).get('controller', {}).get(event.code, None)

            if mapped_button:
                if event.ev_type == "Absolute":
                    await handle_analog_value(mapped_button, event)
                elif event.ev_type == "Key":
                    await handle_button_press(mapped_button, event)
            elif event.ev_type in ("Relative", "Absolute", "Key"):
                print("Found unmapped code \"%s\" %s" % (event.code, event.state))

    async def handle_analog_value(mapped_button, event):
        """send analog value to switch"""
        trigger_below = mapped_button.get("trigger_below", 0)
        trigger_above = mapped_button.get("trigger_above", 100)

        input_pct = event.state / 255
        if mapped_button.get('input') == "h" and mapped_button.get('stick') is not None:
            await switch_controller.stick_h_pct(mapped_button.get('stick'), input_pct)
        elif mapped_button.get('input') == "v" and mapped_button.get('stick') is not None:
            await switch_controller.stick_v_pct(mapped_button.get('stick'), 1-input_pct)
        else:
            # Handle button presses
            pressed = input_pct * 100 > trigger_above or input_pct * 100 < trigger_below
            if button_last_state.get(event.code) == None:
                button_last_state[event.code] = pressed

            if button_last_state.get(event.code) != pressed:
                if pressed:
                    await switch_controller.hold(mapped_button.get('input'))
                else:
                    await switch_controller.release(mapped_button.get('input'))
            button_last_state[event.code] = pressed

    async def handle_button_press(mapped_button, event):
        """Send button presses to switch"""
        stick = mapped_button.get("stick")

        # Handle joystick
        if stick is not None:
            await switch_controller.stick(
                stick, mapped_button.get('input'), not event.state
            )
            return

        # Handle button presses
        if event.state:
            await switch_controller.hold(mapped_button.get('input'))
        else:
            await switch_controller.release(mapped_button.get('input'))

    asyncio.get_event_loop().create_task(listen())
