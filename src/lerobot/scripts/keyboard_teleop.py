"""
Keyboard teleoperation for SO-100 follower arm (no leader required).

Maps KeyboardEndEffectorTeleop deltas to joint goal positions (approximate —
not full Cartesian IK).

Controls:
  Arrow keys       — shoulder pan / shoulder lift
  Shift / Shift-R  — elbow flex
  Ctrl-R / Ctrl-L  — gripper open / close (hold)
  ESC              — quit

Usage (from repo root):
  uv run python src/lerobot/scripts/keyboard_teleop.py

Requires: lerobot[pynput-dep] for keyboard input. On macOS, grant Terminal
Accessibility (and Input Monitoring if prompted) for key events.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig
from lerobot.teleoperators.keyboard import KeyboardEndEffectorTeleop, KeyboardEndEffectorTeleopConfig
from lerobot.utils.robot_utils import precise_sleep
from lerobot.utils.utils import move_cursor_up

if TYPE_CHECKING:
    from lerobot.types import RobotAction, RobotObservation

# ── Configure these for your setup ──────────────────────────────────────────
PORT = "/dev/tty.usbmodem58FA0817631"
ROBOT_ID = "my_follower"
FPS = 30
# Degrees per tick for arm joints; percent per tick for gripper (0–100 scale)
STEP_DEG = 1.5
GRIPPER_STEP = 5.0
# ────────────────────────────────────────────────────────────────────────────


def ee_deltas_to_joint_goals(
    obs: RobotObservation,
    raw: dict[str, float],
    motor_names: tuple[str, ...],
    *,
    step_deg: float,
    gripper_step: float,
) -> RobotAction:
    """Turn keyboard EE deltas into a full joint goal dict for SO100Follower.send_action."""
    dx = float(raw.get("delta_x", 0.0) or 0.0)
    dy = float(raw.get("delta_y", 0.0) or 0.0)
    dz = float(raw.get("delta_z", 0.0) or 0.0)
    g = float(raw.get("gripper", 1.0) or 1.0)

    goals: RobotAction = {f"{m}.pos": float(obs[f"{m}.pos"]) for m in motor_names}

    # Heuristic joint coupling (tune signs if motion feels inverted)
    goals["shoulder_pan.pos"] -= step_deg * dx
    goals["shoulder_lift.pos"] += step_deg * (-dy)
    goals["elbow_flex.pos"] += step_deg * dz

    if "gripper" in raw:
        if g < 0.5:
            goals["gripper.pos"] = max(0.0, goals["gripper.pos"] - gripper_step)
        elif g > 1.5:
            goals["gripper.pos"] = min(100.0, goals["gripper.pos"] + gripper_step)

    return goals


robot = SO100Follower(SO100FollowerConfig(port=PORT, id=ROBOT_ID))
teleop = KeyboardEndEffectorTeleop(
    KeyboardEndEffectorTeleopConfig(id="keyboard_teleop", use_gripper=True),
)
motor_names = tuple(robot.bus.motors.keys())

robot.connect(calibrate=False)
teleop.connect()

print("Keyboard teleop active. ESC to quit.\n")
print(f"{'JOINT':<20} {'TARGET':>8}")
print("-" * 30)

try:
    while teleop.is_connected:
        t0 = time.perf_counter()

        obs = robot.get_observation()
        raw_action = teleop.get_action()
        robot_action = ee_deltas_to_joint_goals(
            obs,
            raw_action,
            motor_names,
            step_deg=STEP_DEG,
            gripper_step=GRIPPER_STEP,
        )
        robot.send_action(robot_action)

        move_cursor_up(len(robot_action) + 1)
        for joint, val in robot_action.items():
            print(f"{joint:<20} {val:>8.1f}")

        precise_sleep(max(1 / FPS - (time.perf_counter() - t0), 0.0))
except KeyboardInterrupt:
    pass
finally:
    teleop.disconnect()
    robot.disconnect()
    print("\nStopped.")
