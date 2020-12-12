import asyncio
import keyboard

loop = asyncio.get_event_loop()


def init_keyboard(switch_controller, configuration={}):
    """Initialize the keyboard handler to translate keyboard buttons to controller input"""
    button_last_state = {}

    async def handle_key_change(keyboard_event):
        mapped_button = configuration.get("button_mapping", {}).get('keyboard', {}).get(keyboard_event.name, {'buttons': [keyboard_event.name]}).copy()
        mapped_button['release'] = mapped_button.get('release', (keyboard_event.event_type == "up"))
        mapped_button['buttons'] = mapped_button.get('buttons', mapped_button.get("input"))

        stick = mapped_button.get("stick")

        # Handle joystick
        if stick is not None:
            mapped_button['side'] = mapped_button.get('side', stick)
            mapped_button['pct'] = None if mapped_button.get('release') else mapped_button.get('pct')
            mapped_button['direction'] = mapped_button.get('direction', mapped_button.get("input"))

        await switch_controller.handle(**mapped_button)

    def keyboard_handler(keyboard_event):
        if button_last_state.get(keyboard_event.name) == None:
            button_last_state[keyboard_event.name] = (
                "up" if keyboard_event.event_type == "down" else "down"
            )
        if button_last_state.get(keyboard_event.name) != keyboard_event.event_type:
            loop.create_task(handle_key_change(keyboard_event))
            button_last_state[keyboard_event.name] = keyboard_event.event_type

    keyboard.hook(keyboard_handler)
