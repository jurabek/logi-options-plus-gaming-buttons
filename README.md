# Logi Options+ extra-button switch

Manual off/on switch for extra MX Master buttons. Run it before gaming, then turn the buttons back on when you are done.

It does not detect games and does not follow the foreground app. Off disables the extra controls on every stored Options+ profile until you turn them back on. Left click, right click, and the vertical wheel stay active.

Current state is on (`state.json` has `"disabled": false`).

## Usage

Before gaming:

```bat
.\logi-options-plus-gaming-buttons\buttons-off.cmd
```

When finished:

```bat
logi-options-plus-gaming-buttons\buttons-on.cmd
```

Or from this folder:

```bat
python buttons.py off
python buttons.py on
python buttons.py status
```

Each off/on command stops `logioptionsplus_agent.exe`, edits `%LOCALAPPDATA%\LogiOptionsPlus\settings.db`, then starts the agent again. The Options+ local pipe does not accept outside clients, so the database edit plus restart is how the change is applied. Expect Options+ to restart for a few seconds.

Do not run off twice. If the buttons are already off, off does nothing.

## What off disables

On every stored profile, including Desktop, Edge, and CoD:

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

Those slots are set to the shipped cards `card_global_presets_do_nothing` and `card_global_presets_thumbwheel_do_nothing`. `buttons.py on` puts the previous assignments back from `state.json`.

## Files

| File | Role |
| --- | --- |
| `buttons-off.cmd` | Runs `buttons.py off` |
| `buttons-on.cmd` | Runs `buttons.py on` |
| `buttons.py` | Stops the agent, edits settings, starts the agent |
| `state.json` | Remembers whether buttons are off and stores the assignments to restore |
| `backups\settings-before-off-20261102-173131.json` | Full settings snapshot taken before an off |
| `CHANGES.md` | Record of the switch and the removed game-detection setup |

No file under `C:\Program Files\LogiOptionsPlus` is modified.

## If on cannot restore

1. Stop `logioptionsplus_agent.exe`.
2. Replace the `file` blob in `%LOCALAPPDATA%\LogiOptionsPlus\settings.db` with the newest `backups\settings-before-off-*.json`.
3. Start `C:\Program Files\LogiOptionsPlus\logioptionsplus_agent.exe`.
4. Set `state.json` to `{"disabled": false, "profiles": {}}` so the next off can save a fresh copy.

## What this replaced

An earlier version registered executables under `C:\Games` and Steam, and a foreground mouse hook started with Windows. That game detection was removed. Original profiles were restored, including the CoD profile `3832e2ba-8e48-4aa6-8d20-9fa192b8c2c0`. Details are in `CHANGES.md`.
