import yaml


def get():
    with open(r"config.yaml") as file:
        configuration = yaml.load(file, Loader=yaml.FullLoader)
    if configuration == None:
        configuration = {}

    configuration["reconnect_bt_addr"] = configuration.get("reconnect_bt_addr")
    configuration["button_mapping"] = configuration.get(
        "button_mapping",
        {
            "w": {"stick": "left", "input": "up"},
            "a": {"stick": "left", "input": "left"},
            "s": {"stick": "left", "input": "down"},
            "d": {"stick": "left", "input": "right"},
            "8": {"stick": "right", "input": "up"},
            "4": {"stick": "right", "input": "left"},
            "2": {"stick": "right", "input": "down"},
            "6": {"stick": "right", "input": "right"},
            "space": {"input": "a"},
            "enter": {"input": "a"},
            "backspace": {"input": "b"},
            "n": {"input": "nfc"},
        },
    )

    return configuration


def save(configuration):
    with open(r"config.yaml", "w") as file:
        yaml.dump(configuration, file)
