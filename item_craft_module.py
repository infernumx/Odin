import pyautogui
import re
import time
from mytypes import Position
from bot_controller import Bot
from loguru import logger

# TODO: implement crafting 'blueprints' alt/regal/alch etc for fully fledged crafting
# TODO: implement delve crafting (pick out resonators -> put fossil in -> craft)


def process_item(item_info: str) -> list[str]:
    info = item_info.split("--------")
    if len(info) < 2:
        return []
    mods = [mod for mod in info[-2].strip().split("\n") if not mod.startswith("(")]
    return mods


def filter_mods_by_regex(
    match_any_mod: bool,
    mods: list[str],
    regexes: list[str],
    matching_tiers: list[tuple[int, bool]],
) -> bool:
    matched = 0
    for tier, modtext in zip(mods[::2], mods[1::2]):
        for i, regex in enumerate(regexes):
            if re.search(regex, modtext.lower()):
                logger.info(f"Regex found, {regex}; {modtext}")
                if _tier := re.search(r"Tier: (\d+)", tier):
                    tier_number = int(_tier.group(1))
                    matching_tier, gthan = matching_tiers[i]
                    if (gthan and tier_number <= matching_tier) or (
                        tier_number == matching_tier
                    ):
                        matched += 1
    return (match_any_mod and matched > 0) or (matched == len(regexes))


def craft_item(regexes: list[str], match_any_mod: bool) -> None:
    real_regexes = []
    matching_tiers = []
    for regex in regexes:
        if re.search(r"\[(\d+\+?)\]", regex):
            rgx = regex[: regex.rfind("[")]
            tier = regex[regex.rfind("[") + 1 : regex.rfind("]")]
            if tier[-1] == "+":
                matching_tiers.append((int(tier[:-1]), True))
            else:
                matching_tiers.append((int(tier), False))
            real_regexes.append(rgx)
        else:
            matching_tiers.append((1, False))
            real_regexes.append(regex)

    while not Bot.get_killswitch_state():
        method_pos: Position = Bot.get_global("craft-method")
        item_pos: Position = Bot.get_global("craft-item")
        item_info: str = Bot.get_item_info(item_pos)
        mods: list[str] = process_item(item_info)
        logger.info(regexes)
        logger.info(item_info)
        logger.info(mods)
        if not mods:
            return
        if filter_mods_by_regex(match_any_mod, mods, real_regexes, matching_tiers):
            return
        if not method_pos or not item_pos:
            return
        pyautogui.moveTo(method_pos.x, method_pos.y)
        pyautogui.rightClick()
        pyautogui.moveTo(item_pos.x, item_pos.y)
        pyautogui.leftClick()
        time.sleep(0.10)
