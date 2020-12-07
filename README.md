# Joycon controller
Have you ever wanted to use your keyboard or any other controller as a switch controller?
Now you can by using this!

NOTE: This package is simply a wrapper around https://github.com/mart1nro/joycontrol
to read and parse the input and send this to joycontrol

## Installation
 - Run `git clone --recurse-submodules https://github.com/indykoning/joycon-controller`
 - Move into the joycontrol folder
 - Folow the installation instructions for joycontrol in https://github.com/mart1nro/joycontrol#installation
 - Install the requirements for this package `sudo pip3 install -r requirements.txt`
 - Thats it! now you can run `sudo python3 index.py`

## Configuration
This module comes with a handy config.yaml file.
Here you can set up key bindings and set the "reconnect_bt_addr"

Explanation of the mapping
```yaml
button_mapping:
  keyboard:
    backspace: # Backspace keyboard button
      input: b # The joycon button "B"
    n: # "n" keyboard button
      input: nfc # Reload the NFC file in the nfc folder
    w: # "w" keyboard button
      input: up # Input on a joystick
      stick: left # The side of the joystick
reconnect_bt_addr: 00:00:00:00:00:00 # The MAC adress of the switch, after initial connection this allows it to connect automatically

```

| Type           | Available buttons |
|----------------|-------------------|
| input (button) | a                 |
|                | b                 |
|                | x                 |
|                | y                 |
|                | l                 |
|                | zl                |
|                | r                 |
|                | zr                |
|                | minus             |
|                | plus              |
|                | r_stick           |
|                | l_stick           |
|                | home              |
|                | capture           |
|                | down              |
|                | up                |
|                | right             |
|                | left              |
|                |                   |
| stick          | left              |
|                | right             |
|                |                   |
| input (stick)  | up                |
|                | down              |
|                | left              |
|                | right             |
