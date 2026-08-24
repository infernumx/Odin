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

## Website Socket.IO Integration

Odin bot runs outside website repository. Website is relay and persistent state store; bot must never receive browser session cookies.

### Connection and Isolation

- Endpoint: `https://poop.agency/socket.io`; server URL: `https://poop.agency`.
- Connect a `socketio.Client(reconnection=True)` to namespace `/bot` with `auth={"api_key": ...}`.
- Bot events always use `/bot`; browser events use `/`. Invalid or missing API key rejects connection.
- One bot per API key. A replacement connection disconnects prior bot.
- Server maps each API key to one live bot SID, private browser room `odin:user:<api-key>`, persisted calibrations, and killswitch state.
- Route browser commands only to same user's bot; route bot updates only to same user's browser tabs. Never broadcast globally or route to a first-connected bot.
- Persist calibrations and killswitch across server restarts. Never persist Socket.IO SIDs.
- Reconnect automatically, handle disconnects, treat non-empty server calibration state as authoritative, and never log API keys. Browser-facing bot text must be plain status/data, never trusted HTML.

### Lifecycle and Commands

On connection, server emits `load_calibrations` on `/bot` with `{item: {x, y}}`; bot loads that state. Server also sends browser bot connection state, killswitch state, and full calibration state.

Bot receives these `/bot` commands:

| Event | Payload |
| --- | --- |
| `load_calibrations` | `{item: {x, y}}` |
| `capture_coordinates` | `{item}` |
| `start_cluster_crafting` | `{regexes: string[]}` |
| `stop_cluster_crafting` | none |
| `start_single_map_crafting` | map settings |
| `start_bulk_map_crafting` | map settings plus grid fields |
| `stop_map_crafting` | none |
| `start_item_crafting` | `{steps}` |
| `stop_item_crafting` | none |

For `capture_coordinates`, read requested game position, then emit `calibration_data` on `/bot` as `{"item": item, "x": x, "y": y}`.

Known calibration IDs:

- Currencies: `orb_of_scouring`, `orb_of_alchemy`, `exalted_orb`, `orb_of_annulment`, `orb_of_alteration`, `orb_of_transmutation`, `regal_orb`, `chaos_orb`, `orb_of_augmentation`
- Tasks: `cluster_jewel_item`, `horticraft_craft_button`, `map_item`, `inventory_top_left`, `item_to_craft`

### Browser Updates

Emit all bot updates on `/bot`. Server relays them to same user's browser tabs:

| Bot event | Browser event |
| --- | --- |
| `calibration_data` | `calibration_result` |
| `killswitch_toggled` | `killswitch_status_changed` |
| `crafting_update` | `cluster_update`, `crafting_attempt` |
| `crafting_success` | `crafting_success` |
| `crafting_finished` | `crafting_finished` |
| `crafting_status` | `crafting_status` |
| `map_check_data`, `map_crafting_update` | `map_crafting_update` |
| `map_crafting_attempt`, `map_crafting_status`, `map_crafting_success`, `map_crafting_finished`, `bulk_crafting_update` | same event name |
| `item_crafting_update`, `item_crafting_status`, `item_crafting_finished` | same event name |

Emit killswitch changes as `sio.emit("killswitch_toggled", {"active": True}, namespace="/bot")`.

### Payload Contracts

Map settings contain `unwanted_regex`, `wanted_regex`, `max_attempts`, `target_stats` for Item Quantity, Item Rarity, Monster Pack Size, More Currency, More Maps, and More Scarabs; plus `is_t17_craft` and `implicit_count`. Bulk maps also contain integer `cell_width`, `cell_height`, and `map_count`.

Item crafting uses `{ "steps": [...] }`. Each step contains `method`, `conditions`, `onSuccess`, and `onFailure`. Conditions support AND, OR, NOT, and COUNT groups. Leaves are `regex`, `prefix_count`, `suffix_count`, or `affix_count`; goto targets are one-based step numbers.

Current server-contract sources live outside this repository: `events/web_events.py` (browser to bot), `events/bot_events.py` (bot to browser), and `events/__init__.py` (state and isolation).

## Pi Change Tracking

`agents.md` requires each Pi-made change to be recorded in `changelog.md` under `Unreleased` during same change.
