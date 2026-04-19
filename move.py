"""
Move the SO-100 follower arm to named preset positions.

Usage:
  uv run python move.py

At the prompt:
  A        -> move to position A at default speed
  B 3      -> move to position B at speed 3 (1=slow, 10=fast)
  list     -> show all positions + current joint values
  q        -> quit
"""

import threading

from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig
from lerobot.utils.robot_utils import precise_sleep

# ── Configure these ──────────────────────────────────────────────────────────
PORT = "/dev/tty.usbmodem58FA0817631"
ROBOT_ID = "my_follower"
FPS = 60
DEFAULT_SPEED = 5
# ────────────────────────────────────────────────────────────────────────────

# ── Preset positions (joints in degrees, gripper 0=closed / 100=open) ───────
# Type 'list' at the prompt to see current values — copy them to add new ones.
POSITIONS = {
    "home": {
        "shoulder_pan.pos":   0.0,
        "shoulder_lift.pos":  0.0,
        "elbow_flex.pos":     0.0,
        "wrist_flex.pos":     0.0,
        "wrist_roll.pos":     0.0,
        "gripper.pos":       50.0,
    },
    "A": {
        "shoulder_pan.pos":  30.0,
        "shoulder_lift.pos": -20.0,
        "elbow_flex.pos":    45.0,
        "wrist_flex.pos":    10.0,
        "wrist_roll.pos":     0.0,
        "gripper.pos":       20.0,
    },
    "B": {
        "shoulder_pan.pos": -30.0,
        "shoulder_lift.pos": -20.0,
        "elbow_flex.pos":    45.0,
        "wrist_flex.pos":    10.0,
        "wrist_roll.pos":     0.0,
        "gripper.pos":       20.0,
    },
    "C": {
        "shoulder_pan.pos":   0.0,
        "shoulder_lift.pos": -40.0,
        "elbow_flex.pos":    70.0,
        "wrist_flex.pos":    20.0,
        "wrist_roll.pos":     0.0,
        "gripper.pos":       80.0,
    },
}
# ────────────────────────────────────────────────────────────────────────────


def speed_to_step(speed: int) -> float:
    """Speed 1–10 → degrees per control step."""
    return 0.5 + (speed - 1) * (9.5 / 9)


def move_to(robot, target, step_deg, cancel: threading.Event):
    """Smoothly interpolate to target in a background thread. Stops if cancel is set."""
    while not cancel.is_set():
        obs = robot.get_observation()
        current = {k: obs[k] for k in target}
        deltas = {k: target[k] - current[k] for k in target}
        max_delta = max(abs(d) for d in deltas.values())

        if max_delta < 0.2:
            robot.send_action(target)
            break

        scale = min(step_deg / max_delta, 1.0)
        robot.send_action({k: current[k] + deltas[k] * scale for k in target})
        precise_sleep(1 / FPS)


robot = SO100Follower(SO100FollowerConfig(port=PORT, id=ROBOT_ID))
robot.connect()

names = ", ".join(POSITIONS)
print(f"Ready. Positions: {names}")
print("Type a position (e.g. 'A') or 'A 3' for speed 1-10. 'list' to inspect. 'q' to quit.\n")

cancel_event = threading.Event()
move_thread = None

try:
    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            break

        if not raw:
            continue

        if raw.lower() == "q":
            break

        if raw.lower() == "list":
            print(f"\n{'Position':<10} {'shoulder_pan':>12} {'shoulder_lift':>13} {'elbow_flex':>10} {'wrist_flex':>10} {'wrist_roll':>10} {'gripper':>8}")
            print("-" * 75)
            for name, pos in POSITIONS.items():
                vals = list(pos.values())
                print(f"{name:<10} {vals[0]:>12.1f} {vals[1]:>13.1f} {vals[2]:>10.1f} {vals[3]:>10.1f} {vals[4]:>10.1f} {vals[5]:>8.1f}")
            obs = robot.get_observation()
            vals = list(obs.values())
            print(f"\n{'[current]':<10} {vals[0]:>12.1f} {vals[1]:>13.1f} {vals[2]:>10.1f} {vals[3]:>10.1f} {vals[4]:>10.1f} {vals[5]:>8.1f}\n")
            continue

        parts = raw.split()
        name = parts[0].upper()
        if name not in POSITIONS:
            name = parts[0]
        if name not in POSITIONS:
            print(f"  Unknown: '{parts[0]}'. Available: {names}")
            continue

        speed = DEFAULT_SPEED
        if len(parts) > 1:
            try:
                speed = max(1, min(10, int(parts[1])))
            except ValueError:
                print("  Speed must be 1–10. Using default.")

        # Cancel any in-progress movement and wait for it to stop
        cancel_event.set()
        if move_thread and move_thread.is_alive():
            move_thread.join()
        cancel_event.clear()

        print(f"  → {name}  (speed {speed}/10)")
        move_thread = threading.Thread(
            target=move_to,
            args=(robot, POSITIONS[name], speed_to_step(speed), cancel_event),
            daemon=True,
        )
        move_thread.start()

except KeyboardInterrupt:
    pass
finally:
    cancel_event.set()
    if move_thread and move_thread.is_alive():
        move_thread.join()
    robot.disconnect()
    print("\nDisconnected.")
