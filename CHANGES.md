# Logi Options+ extra-button switch

Manual off/on only. It does not detect games and does not follow the foreground app.

Before gaming, run:

`C:\Users\Jurabek\dev\logi-options-plus-gaming-buttons\buttons-off.cmd`

When finished, run:

`C:\Users\Jurabek\dev\logi-options-plus-gaming-buttons\buttons-on.cmd`

Off disables extra controls everywhere until you turn them back on. Left click, right click, and the vertical wheel stay active.

## What off disables

On every stored Options+ profile, including Desktop, Edge, and CoD:

| Device | Slot | Control |
| --- | --- | --- |
| MX Master 3S `mx-master-3s-2b034` | `c195` | Gesture |
| MX Master 3S | `c196` | Mode shift |
| MX Master 3S | `c82` | Middle button |
| MX Master 3S | `c83` | Back |
| MX Master 3S | `c86` | Forward |
| MX Master 3S | `thumb_wheel_adapter` | Horizontal thumb wheel |
| MX Master 4 `mx-master-4-2b042` | `c195` | Gesture |
| MX Master 4 | `c196` | Mode shift |
| MX Master 4 | `c416` | Radial menu |
| MX Master 4 | `c82` | Middle button |
| MX Master 4 | `c83` | Back |
| MX Master 4 | `c86` | Forward |
| MX Master 4 | `thumb_wheel_adapter` | Horizontal thumb wheel |

Those slots are set to the shipped cards `card_global_presets_do_nothing` and `card_global_presets_thumbwheel_do_nothing`.

## Files in this folder

- `buttons-off.cmd` runs `buttons.py off`
- `buttons-on.cmd` runs `buttons.py on`
- `buttons.py` stops `logioptionsplus_agent.exe`, edits settings, then starts the agent again
- `state.json` is created on the first off and holds the previous assignments so on can restore them
- `backups\settings-before-off-*.json` is a full settings snapshot taken before the first off

The agent local pipe does not accept outside clients, so the database edit plus restart is how the change is applied. Each command restarts Options+.

## Removed

The earlier game-folder profiles, the foreground mouse hook, and the Startup launcher were removed.

Removed:

- `C:\Users\Jurabek\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\LogiGamingButtons.cmd`
- `C:\Users\Jurabek\AppData\Local\LogiGamingButtons\apply_game_profiles.py`
- `C:\Users\Jurabek\AppData\Local\LogiGamingButtons\gaming_button_filter.py`
- `C:\Users\Jurabek\AppData\Local\LogiGamingButtons\restart_and_apply.py`
- `C:\Users\Jurabek\AppData\Local\LogiGamingButtons\registered-games.txt`
- the running `pythonw.exe` filter (PID 2744)

Original profiles were put back from the settings snapshot taken before those game profiles were written. After that restore, the database again had the CoD profile `3832e2ba-8e48-4aa6-8d20-9fa192b8c2c0`, and the desktop back button was `card_global_presets_win_back`.

No file under `C:\Program Files\LogiOptionsPlus` was modified.

## If on cannot restore

Stop `logioptionsplus_agent.exe`, replace the `file` blob in `settings.db` with the newest `backups\settings-before-off-*.json`, then start:

`C:\Program Files\LogiOptionsPlus\logioptionsplus_agent.exe`

Do not run off twice. If `state.json` says buttons are already off, off does nothing.
