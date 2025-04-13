import pyautogui
import config
import pygetwindow as gw
from pynput import mouse
from bot_controller import Bot


clicked_pos = {"x": 0, "y": 0}


def on_click(x, y, button, pressed) -> bool:
    global clicked_pos
    clicked_pos = {"x": x, "y": y}
    return False


def calibrate(currencyName) -> dict | None:
    if not Bot.activate_poe():
        return None
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    config.set_value(clicked_pos, "currency", currencyName)
    return clicked_pos


def calibrate_cluster_craft_button() -> dict | None:
    if not Bot.activate_poe():
        return None
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    config.set_value(clicked_pos, "cluster", "button-location")
    return clicked_pos
