import pyautogui
import pyperclip
import pygetwindow as gw
from loguru import logger
from pynput import mouse
from mytypes import Position
from typing import Any
import sys

pyautogui.PAUSE = 0.05  # Example: reduce delay to 10ms


class Bot:
    _SIGNALS_ = {}
    _GLOBALS_ = {}

    @classmethod
    def get_global(cls, key) -> Any:
        return Bot._GLOBALS_.get(key)

    @classmethod
    def activate_poe(cls) -> bool:
        if poe_windows := gw.getWindowsWithTitle("Path of Exile"):
            poe = poe_windows[0]
            if not poe.isActive:
                pyautogui.press("altleft")
                poe.activate()
            return True
        return False

    @classmethod
    def get_item_info(cls, pos: Position, retries=0) -> str:
        pyperclip.copy("")
        if not cls.activate_poe():
            logger.error("Could not activate PoE")
            return ""
        pyautogui.moveTo(pos.x, pos.y)
        pyautogui.hotkey("ctrl", "alt", "c")
        ret = pyperclip.paste().replace("\r\n", "\n")
        if not ret and retries < 3:
            return Bot.get_item_info(pos, retries=retries + 1)
        return ret

    @classmethod
    def select_pos(cls, key: str = "SELECTPOS") -> Position | None:
        if not cls.activate_poe():
            return None

        def click_callback(x, y, button, pressed) -> bool:
            Bot._GLOBALS_[key] = Position(x, y)
            return False

        with mouse.Listener(on_click=click_callback) as listener:
            listener.join()
        return Bot._GLOBALS_.get(key)

    @classmethod
    def toggle_killswitch(cls):
        cls._SIGNALS_["KILLSWITCH"] = not cls.get_killswitch_state()
        logger.info(f"Killswitch state set to {cls.get_killswitch_state()}")

    @classmethod
    def get_killswitch_state(cls):
        return cls._SIGNALS_.get("KILLSWITCH", False)


logger.add(
    sys.stderr, format="{time} {level} {message}", filter="bot_controller", level="INFO"
)
