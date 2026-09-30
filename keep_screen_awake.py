#!/usr/bin/env python3
"""
Keep the screen awake on macOS.

Default mode uses `caffeinate` (works for standard users, no admin needed).

Optional mouse mode moves the cursor in a loop, but macOS blocks that unless
Terminal/Cursor has Accessibility permission:
  System Settings -> Privacy & Security -> Accessibility

Press Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time

MOVE_DURATION = 0.8
MARGIN = 100
CYCLE_PAUSE = 1.0


def mouse_control_allowed() -> bool:
    import pyautogui

    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0

    before = pyautogui.position()
    target_x = max(0, before.x + 8)
    pyautogui.moveTo(target_x, before.y, duration=0)
    after = pyautogui.position()
    pyautogui.moveTo(before.x, before.y, duration=0)
    return after.x != before.x or after.y != before.y


def get_positions() -> dict[str, tuple[int, int]]:
    import pyautogui

    width, height = pyautogui.size()
    center_x = width // 2
    center_y = height // 2

    return {
        "left": (MARGIN, center_y),
        "right": (width - MARGIN, center_y),
        "center": (center_x, center_y),
        "top": (center_x, MARGIN),
        "bottom": (center_x, height - MARGIN),
    }


def run_movement_cycle(positions: dict[str, tuple[int, int]]) -> None:
    import pyautogui

    path = [
        ("left", "right"),
        ("right", "center"),
        ("center", "top"),
        ("top", "bottom"),
        ("bottom", "center"),
        ("center", "left"),
    ]

    for start_name, end_name in path:
        start = positions[start_name]
        end = positions[end_name]
        pyautogui.moveTo(start[0], start[1], duration=0.1)
        pyautogui.moveTo(end[0], end[1], duration=MOVE_DURATION)


def run_mouse_mode() -> None:
    import pyautogui

    if not mouse_control_allowed():
        print("Mouse control is blocked by macOS.")
        print("Grant Accessibility access to this app, then try again:")
        print("  System Settings -> Privacy & Security -> Accessibility")
        print()
        print("Or use the default mode (no permission needed):")
        print("  python3 keep_screen_awake.py")
        sys.exit(1)

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    width, height = pyautogui.size()
    print("Keep Screen Awake - mouse mode")
    print(f"Screen size: {width}x{height}")
    print("Press Ctrl+C to stop.")
    print("Move mouse to any corner to emergency stop.\n")

    positions = get_positions()

    try:
        while True:
            run_movement_cycle(positions)
            time.sleep(CYCLE_PAUSE)
    except KeyboardInterrupt:
        print("\nStopped.")


def run_caffeinate_mode() -> None:
    print("Keep Screen Awake - caffeinate mode")
    print("No admin or Accessibility permission needed.")
    print("Press Ctrl+C to stop.\n")

    process = subprocess.Popen(
        ["caffeinate", "-d", "-i", "-m", "-s"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()


def main() -> None:
    parser = argparse.ArgumentParser(description="Keep the macOS screen awake.")
    parser.add_argument(
        "--mouse",
        action="store_true",
        help="Move the mouse in a loop (requires Accessibility permission).",
    )
    args = parser.parse_args()

    if args.mouse:
        run_mouse_mode()
    else:
        run_caffeinate_mode()


if __name__ == "__main__":
    main()
