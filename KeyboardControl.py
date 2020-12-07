import asyncio
import keyboard

loop = asyncio.get_event_loop()


def init_keyboard(switch_controller, configuration={}):
    """Initialize the keyboard handler to translate keyboard buttons to controller input"""
    button_last_state = {}

    async def handle_key_change(keyboard_event):
        mapped_button = configuration.get("button_mapping", {}).get('keyboard', {}).get(keyboard_event.name)

        # Pass keyboard button if no mapping was found.
        if mapped_button is None:
            button = keyboard_event.name
            stick = None
        else:
            button = mapped_button.get("input")
            stick = mapped_button.get("stick")

        # Handle joystick
        if stick is not None:
            await switch_controller.stick(
                stick, button, keyboard_event.event_type == "up"
            )
            return

        # Reload NFC tag from nfc folder
        if button == "nfc" and keyboard_event.event_type == "down":
            await switch_controller.load_nfc()
            return

        # Normal key press
        if keyboard_event.event_type == "down":
            await switch_controller.hold(button)
        else:
            await switch_controller.release(button)

    def keyboard_handler(keyboard_event):
        if button_last_state.get(keyboard_event.name) == None:
            button_last_state[keyboard_event.name] = (
                "up" if keyboard_event.event_type == "down" else "down"
            )
        if button_last_state.get(keyboard_event.name) != keyboard_event.event_type:
            loop.create_task(handle_key_change(keyboard_event))
            button_last_state[keyboard_event.name] = keyboard_event.event_type

    keyboard.hook(keyboard_handler)
