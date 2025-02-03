import json
import os
from mytypes import Position

CONFIG_FILE = "userconfig.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "cluster": {"button-location": {"x": 0, "y": 0}},
            "currency": {
                "chaos": {"x": 0, "y": 0},
                "augment": {"x": 0, "y": 0},
                "alteration": {"x": 0, "y": 0},
                "scouring": {"x": 0, "y": 0},
            },
        }
        save_config(default_config)
        return default_config
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_value(section, key):
    config = load_config()
    return config.get(section, {}).get(key)


def set_value(value, section, key):
    config_data = load_config()
    if section not in config_data:
        config_data[section] = {}
    config_data[section][key] = value
    save_config(config_data)


def get_value_as_position(section, key):
    val = get_value(section, key)
    if val:
        return Position(val["x"], val["y"])
    return None
