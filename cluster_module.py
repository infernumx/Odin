import pyautogui
import re
import config
import time
from mytypes import Position, Cluster
from bot_controller import Bot
from loguru import logger


def process_cluster(item_info: str) -> Cluster | None:
    jewel_type_match = re.search(r"(\w*) Cluster Jewel\n-{8}", item_info)
    if not jewel_type_match:
        return None
    jewel_type = f"{jewel_type_match.group(1)} Cluster Jewel"
    ilvl = int(re.search(r"Item Level: (\d+)", item_info).group(1))
    passives = int(
        re.search(r"Adds (\d+) Passive Skills \(enchant\)", item_info).group(1)
    )
    jewel_base = re.search(
        r"Added Small Passive Skills grant: ([^\n]+)\n", item_info
    ).group(1)
    mods_match = re.search(
        r"\(enchant\)\n-{8}\n([{}\d\w\s\"(:—),\.\+\-%]*)\n-{8}", item_info, re.DOTALL
    )
    if mods_match:
        mods = mods_match.group(1).split("\n")
        return Cluster(ilvl, passives, jewel_type, jewel_base, mods)
    return None


def filter_mods_by_regex(cluster: Cluster, regexes: list[str]) -> bool:
    matched = 0
    for mod in cluster.mods:
        for regex in regexes:
            if re.search(regex, mod):
                matched += 1
    return matched == len(regexes)


def craft_cluster(
    regexes: list[str], attempt_callback=None, success_callback=None
) -> None:
    location: Position = config.get_value_as_position("cluster", "button-location")
    item_location: Position = Position(location.x, location.y - 80)
    while not Bot.get_killswitch_state():
        item_info: str = Bot.get_item_info(item_location, retries=5)
        cluster = process_cluster(item_info)
        if not cluster:
            logger.info("No cluster info found")
            return
        if filter_mods_by_regex(cluster, regexes):
            logger.info("Matched mods")
            if success_callback:
                success_callback(cluster)
            return
        pyautogui.moveTo(location.x, location.y)
        pyautogui.leftClick()
        if attempt_callback:
            attempt_callback()
        time.sleep(0.1)
