"""Turn extra Logi Options+ mouse buttons off or on.

Run before gaming:
    buttons.py off

Run when finished:
    buttons.py on

This does not look at which app is in front. Off disables the extra controls
everywhere until you turn them back on. Left click, right click, and the
vertical wheel are not changed.

The Options+ agent reloads assignments from settings.db only at startup, and
its local pipe does not accept outside clients. Each command stops the agent,
edits the database, then starts the agent again.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

AGENT = Path(r"C:\Program Files\LogiOptionsPlus\logioptionsplus_agent.exe")
DB = Path.home() / "AppData" / "Local" / "LogiOptionsPlus" / "settings.db"
HERE = Path(__file__).resolve().parent
STATE = HERE / "state.json"
DESKTOP_ID = "420fd454-0c36-499d-bde4-146823b16147"
BUTTON_SUFFIXES = {
    "mx-master-3s-2b034": ("c195", "c196", "c82", "c83", "c86"),
    "mx-master-4-2b042": ("c195", "c196", "c416", "c82", "c83", "c86"),
}

DO_NOTHING = {
    "id": "card_global_presets_do_nothing",
    "name": "ASSIGNMENT_NAME_DONOTHING",
    "attribute": "MACRO_PLAYBACK",
    "readOnly": True,
    "continuous": False,
    "macro": {
        "type": "DO_NOTHING",
        "onboardable": False,
        "actionName": "",
        "icon": "",
        "doNothing": {"action": "NONE"},
    },
    "nestedCards": {},
    "icons": {"uri": "pipeline://system_actions/", "icons": ["DoNothing.png", "DoNothing.svg"]},
    "tags": ["PRESET_TAG_MISC", "PRESET_MOUSE_FUNCTIONS"],
    "taskId": 82,
}
THUMB_NOTHING = {
    "id": "card_global_presets_thumbwheel_do_nothing",
    "name": "ASSIGNMENT_NAME_DONOTHING",
    "attribute": "ADAPTER_2WAYS",
    "readOnly": True,
    "continuous": False,
    "gestureInfo": {"implementation": "CUSTOM_DO_NOTHING"},
    "nestedCards": {},
    "icons": {"uri": "pipeline://system_actions/", "icons": ["DoNothing.png", "DoNothing.svg"]},
    "tags": ["PRESET_TAG_THUMBWHEEL", "PRESET_TAG_ANALOG_CONTROL"],
    "taskId": 82,
}


def extra_slots() -> list[str]:
    slots = []
    for prefix, suffixes in BUTTON_SUFFIXES.items():
        slots.extend(f"{prefix}_{suffix}" for suffix in suffixes)
        slots.append(f"{prefix}_thumb_wheel_adapter")
    return slots


def nothing_assignment(slot_id: str) -> dict:
    card = json.loads(json.dumps(THUMB_NOTHING if slot_id.endswith("thumb_wheel_adapter") else DO_NOTHING))
    return {"card": card, "cardId": card["id"], "slotId": slot_id, "tags": ["UI_PAGE_BUTTONS"]}


def running(image: str) -> bool:
    out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, errors="replace")
    return any(line.lower().startswith(f'"{image.lower()}"') for line in out.splitlines())


def stop_agent() -> None:
    subprocess.run(["taskkill", "/IM", "logioptionsplus_agent.exe", "/F"], check=False, capture_output=True)
    for _ in range(40):
        if not running("logioptionsplus_agent.exe"):
            time.sleep(0.4)
            return
        time.sleep(0.2)
    raise SystemExit("Logi Options+ agent did not exit")


def start_agent() -> None:
    subprocess.Popen([str(AGENT)], close_fds=True)
    for _ in range(40):
        if running("logioptionsplus_agent.exe"):
            print("Options+ agent restarted")
            return
        time.sleep(0.2)
    raise SystemExit("Logi Options+ agent did not start")


def load_db() -> tuple[sqlite3.Connection, dict, int]:
    con = sqlite3.connect(DB)
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    row = con.execute("select _id, file from data").fetchone()
    if not row:
        raise SystemExit(f"no settings row in {DB}")
    blob = row[1]
    if isinstance(blob, str):
        blob = blob.encode()
    return con, json.loads(blob), row[0]


def save_db(con: sqlite3.Connection, data: dict, row_id: int) -> None:
    payload = json.dumps(data, indent=2).encode("utf-8")
    con.execute("update data set file=? where _id=?", (payload, row_id))
    con.commit()
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    con.close()


def profile_keys(data: dict) -> list[str]:
    keys = list(data.get("profile_keys") or [])
    for key in data:
        if key.startswith("profile-") and key not in keys:
            keys.append(key)
    return keys


def read_state() -> dict:
    if not STATE.exists():
        return {"disabled": False, "profiles": {}}
    return json.loads(STATE.read_text(encoding="utf-8"))


def write_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def turn_off() -> None:
    state = read_state()
    if state.get("disabled"):
        print("extra buttons are already off")
        return
    stop_agent()
    con, data, row_id = load_db()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = HERE / "backups" / f"settings-before-off-{stamp}.json"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(json.dumps(data, indent=2), encoding="utf-8")
    saved: dict[str, dict] = {}
    slots = extra_slots()
    for key in profile_keys(data):
        profile = data.get(key)
        if not isinstance(profile, dict):
            continue
        profile.setdefault("assignments", [])
        by_slot = {row.get("slotId"): row for row in profile["assignments"]}
        saved[key] = {slot: by_slot.get(slot) for slot in slots}
        kept = [row for row in profile["assignments"] if row.get("slotId") not in slots]
        kept.extend(nothing_assignment(slot) for slot in slots)
        profile["assignments"] = kept
        data[key] = profile
    save_db(con, data, row_id)
    write_state({"disabled": True, "profiles": saved, "backup": str(backup)})
    start_agent()
    print("extra buttons off")
    print("left, right, and vertical scroll stay on")
    print("run buttons-on.cmd when you are done")


def turn_on() -> None:
    state = read_state()
    if not state.get("disabled"):
        print("extra buttons are already on")
        return
    saved = state.get("profiles") or {}
    stop_agent()
    con, data, row_id = load_db()
    slots = set(extra_slots())
    for key, slot_map in saved.items():
        profile = data.get(key)
        if not isinstance(profile, dict):
            continue
        assignments = [row for row in profile.get("assignments") or [] if row.get("slotId") not in slots]
        for slot, original in slot_map.items():
            if original:
                assignments.append(original)
        profile["assignments"] = assignments
        data[key] = profile
    save_db(con, data, row_id)
    write_state({"disabled": False, "profiles": {}})
    start_agent()
    print("extra buttons on")


def status() -> None:
    state = read_state()
    print("off" if state.get("disabled") else "on")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"off", "on", "status"}:
        raise SystemExit("usage: buttons.py off|on|status")
    if not DB.exists():
        raise SystemExit(f"missing {DB}")
    if not AGENT.exists():
        raise SystemExit(f"missing {AGENT}")
    {"off": turn_off, "on": turn_on, "status": status}[sys.argv[1]]()


if __name__ == "__main__":
    main()
