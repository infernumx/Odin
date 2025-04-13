import pyautogui
import re
import config
import time
from mytypes import Position
from bot_controller import Bot
from loguru import logger
import sys


def process_item(item_info: str) -> tuple[list[str], list[str]]:
    info = item_info.split("--------")
    if not info or len(info) < 3:
        return tuple()
    mods = [mod for mod in info[-3].strip().split("\n") if not mod.startswith("(")]
    implicits = info[1].strip().split("\n")
    return mods, implicits


CONST_IMPLICITS = (
    "Item Quantity",
    "Item Rarity",
    "Monster Pack Size",
    "More Maps",
    "More Scarabs",
    "More Currency",
)


def filter_implicits(item_implicits: list[str], expected_implicits: dict) -> bool:
    matched = {}
    for implicit in CONST_IMPLICITS:
        for mod in item_implicits:
            r = re.search(rf"{implicit}: \+(\d+)%", mod)
            if r:
                matched[implicit] = int(r.group(1))
    return all(
        matched.get(_type, 0) >= value
        for _type, value in expected_implicits.items()
        if value > 0
    )


def filter_mods_by_regex(regex_count: int, mods: list[str], regexes: list[str]) -> bool:
    matched = 0
    for modtext in mods:
        for regex in regexes:
            if re.search(regex, modtext):
                matched += 1
    return matched == regex_count


def craft_map(regexes: list[str], regex_count: int, expected_implicits: dict) -> None:
    method_pos: Position | None = config.get_value_as_position("currency", "chaos")
    map_pos: Position = Bot.get_global("map-item")
    if not method_pos or not map_pos:
        logger.info("Method pos or Map pos not set")
        return
    while not Bot.get_killswitch_state():
        item_info: str = Bot.get_item_info(map_pos)
        processed = process_item(item_info)
        if not processed:
            continue
        mods: list[str] = processed[0]
        implicits: list[str] = processed[1]
        if not mods:
            logger.info("Could not find processed mods")
            return
        if filter_mods_by_regex(regex_count, mods, regexes) and filter_implicits(
            implicits, expected_implicits
        ):
            logger.info("Regexes matched")
            return
        pyautogui.moveTo(method_pos.x, method_pos.y)
        pyautogui.rightClick()
        pyautogui.moveTo(map_pos.x, map_pos.y)
        pyautogui.leftClick()


logger.add(
    sys.stderr, format="{time} {level} {message}", filter="map_module", level="INFO"
)
