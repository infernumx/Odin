# Project Context

## Purpose

Odin is a Windows-focused PySide6 desktop app that automates Path of Exile crafting workflows. It reads copied in-game item text, evaluates user regexes and map implicit thresholds, then uses PyAutoGUI to apply currencies until a match or killswitch stop. It also connects to its companion website through Socket.IO.

## Runtime

- Python 3.10+
- UI: PySide6
- Automation: PyAutoGUI, PyGetWindow, pynput, keyboard
- Item clipboard reads: pyperclip
- Logging: loguru
- Website connection: Socket.IO
- Dependencies: pinned in `requirements.txt`
- Start: `python main.py`

## Layout

- `main.py`: app bootstrap, sidebar, page wiring, global `+` killswitch monitor.
- `bot_controller.py`: Path of Exile window activation, clipboard item capture, position selection, killswitch state.
- `config.py`: persistent calibration in ignored `userconfig.json`.
- `calibration_module.py`: currency and cluster-button coordinate capture.
- `cluster_module.py`, `map_module.py`, `item_craft_module.py`: parsing, filtering, and automation loops.
- `mytypes.py`: `Position` and `Cluster` dataclasses.
- `theme.py`: Qt stylesheet and header helpers.
- `pages/`: calibration, clusters, maps, items, and settings widgets.
- `images/`: UI and currency assets.

## Data Flow

1. User calibrates inventory and crafting coordinates.
2. UI starts a daemon crafting thread.
3. Module activates Path of Exile, captures item text with `Ctrl+Alt+C`, parses mods, and evaluates configured filters.
4. Module clicks currency and target until match, failure limit, or killswitch.

## Constraints

- Path of Exile must be running and recognizable by its window title.
- Screen coordinates depend on user calibration and display scaling.
- Regex input is user-supplied; preserve current matching behavior unless task explicitly changes it.
- UI updates from worker threads exist in current design; avoid broad concurrency refactors without a concrete bug.
- No test suite or packaging config currently exists.

## Pi Change Tracking

`agents.md` requires each Pi-made change to be recorded in `changelog.md` under `Unreleased` during same change.
