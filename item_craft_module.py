import pyautogui
import re
import time
from dataclasses import dataclass
from mytypes import Position
from bot_controller import Bot
from loguru import logger
import config

# TODO: implement crafting 'blueprints' alt/regal/alch etc for fully fledged crafting
# TODO: implement delve crafting (pick out resonators -> put fossil in -> craft)


@dataclass
class CraftingStep:
    condition_regex: str  # Regex pattern to check against the item mods
    currency: str  # Currency Method
    on_failure: int = -1  # Step to refer back to on current step's failure
    on_success: int = 0  # Step to continue to
    auto_success: bool = (
        False  # Auto Success (require no regex, example: transmute, scouring)
    )
    max_attempts: int = 10  # Maximum attempts for this step


def process_item_info(item_info: str) -> list[str]:
    """
    Process the item info text and extract a list of mods.
    Assumes that mods are in the second-to-last block of text.
    """
    info = item_info.split("--------")
    if len(info) < 2:
        return []
    mods = [mod for mod in info[-2].strip().split("\n") if not mod.startswith("(")]
    return mods


def craft_item_advanced(steps: list[CraftingStep], counter=0) -> None:
    """
    Automates item crafting using a sequence of steps.
    For each step, repeatedly perform the crafting method until the condition (regex match)
    is met or max_attempts is reached.
    """
    # Retrieve the global item position used for extracting item info.
    item_pos = Bot.get_global("craft-item")
    if not item_pos:
        logger.error("Item position not set.")
        return

    if counter >= len(steps):
        logger.info("Crafting sequence finished")
        return
    step = steps[counter]

    # Get initial item info.
    item_info = Bot.get_item_info(item_pos)
    mods = process_item_info(item_info)

    attempts = 0
    # Continue the step until the condition is met or max_attempts reached.
    while attempts < step.max_attempts and not Bot.get_killswitch_state():
        # Check if any mod matches the condition for this step.
        if any(re.search(step.condition_regex, mod, re.IGNORECASE) for mod in mods):
            logger.info(f"Step condition met: {step.condition_regex}")
            break  # Proceed to next step.
        # Execute the crafting method for this step.
        method_position = currency_pos_lookup(step.currency)
        if not method_position:
            continue
        pyautogui.moveTo(method_position.x, method_position.y)
        pyautogui.rightClick()
        pyautogui.moveTo(item_pos.x, item_pos.y)
        pyautogui.leftClick()
        attempts += 1
        time.sleep(0.1)
        # Update item info and mods after the crafting action.
        item_info = Bot.get_item_info(item_pos)
        mods = process_item_info(item_info)
    else:
        # If the while loop completes without a break, the condition was never met.
        logger.info(f"Step failed after {attempts} attempts: {step.condition_regex}")
        if step.on_failure != -1:
            return craft_item_advanced(steps, counter=step.on_failure)
        return  # Exit the crafting sequence.
    craft_item_advanced(steps, counter=step.on_success)


def currency_pos_lookup(method: str) -> Position | None:
    if not (value := config.get_value_as_position("currency", method)):
        logger.error(f"Calibration for {method} not set.")
        return None

    return value


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
        method_pos: Position = currency_pos_lookup()
        item_pos: Position = Bot.get_global("craft-item")
        item_info: str = Bot.get_item_info(item_pos)
        mods: list[str] = process_item_info(item_info)
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
