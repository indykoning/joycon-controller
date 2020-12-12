from inputs import get_gamepad, UnpluggedError
import asyncio


def init_gamepad(switch_controller, configuration={}):
    """initialize everything for gamepad support"""
    button_last_state = {}
    last_analog_state = {}

    async def listen():
        """Loop forever to listen to gamepad events"""
        try:
            while True:
                await process_gamepad()
        except UnpluggedError:
            pass

    async def process_gamepad():
        """Wait for gamepad event and handle them"""
        events = await asyncio.get_event_loop().run_in_executor(None, get_gamepad)
        for event in events:
            mapped_button = configuration.get("button_mapping", {}).get('controller', {}).get(event.code, {}).copy()

            if mapped_button:
                if event.ev_type == "Absolute":
                    await handle_analog_value(mapped_button, event)
                elif event.ev_type == "Key":
                    await handle_button_press(mapped_button, event)
            elif event.ev_type in ("Relative", "Absolute", "Key"):
                print("Found unmapped code \"%s\" %s" % (event.code, event.state))

    async def handle_analog_value(mapped_button, event):
        """send analog value to switch"""
        # analog_diff = abs(event.state - last_analog_state.get(event.code, event.state))
        if event.state < (255/2) + 20 and event.state > (255/2) - 20:
            if last_analog_state.get(event.code) == 127.5:
                return
            event.state = 127.5
        last_analog_state[event.code] = event.state

        mapped_button['angle'] = mapped_button.get('angle', mapped_button.get('input'))
        mapped_button['side'] = mapped_button.get('side', mapped_button.get('stick'))
        mapped_button['pct'] = event.state / 255

        if not mapped_button.get('side'):
            # Handle button presses
            trigger_below = mapped_button.get("trigger_below", 0)
            trigger_above = mapped_button.get("trigger_above", 100)

            pressed = mapped_button.get('pct') * 100 > trigger_above or mapped_button.get('pct') * 100 < trigger_below
            if button_last_state.get(event.code) is None:
                button_last_state[event.code] = pressed

            if button_last_state.get(event.code) != pressed:
                mapped_button['release'] = not pressed
                mapped_button['buttons'] = mapped_button.get('input')
            button_last_state[event.code] = pressed
        await switch_controller.handle(**mapped_button)

    async def handle_button_press(mapped_button, event):
        """Send button presses to switch"""
        stick = mapped_button.get("stick")

        # Handle joystick
        if stick is not None:
            mapped_button['direction'] = mapped_button.get('direction', mapped_button.get('input'))
        else:
            # Handle button presses
            mapped_button['buttons'] = mapped_button.get('input')

        mapped_button['release'] = not event.state
        await switch_controller.handle(**mapped_button)

    asyncio.get_event_loop().create_task(listen())
