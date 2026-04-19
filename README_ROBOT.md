# SO-100 Robot Arm — Hackathon Setup

## Hardware
- SO-100 follower arm (no leader arm)
- Connected via USB

## Setup

### 1. Install dependencies
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python deps
uv sync --locked --extra core_scripts
uv pip install -e ".[feetech]"
```

### 2. Find your USB port
```bash
uv run lerobot-find-port
```
Update the `PORT` variable at the top of `move.py` and `keyboard_teleop.py` with your port.

### 3. Calibrate (first time only)
```bash
uv run lerobot-calibrate \
    --robot.type=so100_follower \
    --robot.port=/dev/tty.usbmodem585A0076841 \
    --robot.id=my_follower
```
- Move arm to middle of range → press Enter
- Move each joint through full range → press Enter

Calibration saves to `~/.cache/huggingface/lerobot/calibration/robots/so_follower/my_follower.json`

---

## Move to preset positions

```bash
uv run python move.py
```

At the prompt:
- `A` — move to position A
- `B 3` — move to position B at speed 3 (1=slow, 10=fast)
- `list` — show all positions + current joint values
- `q` — quit

Edit the `POSITIONS` dict in `move.py` to add/change positions.

---

## Keyboard teleoperation

```bash
uv run python keyboard_teleop.py
```

- `↑ ↓ ← →` — move end-effector X/Y
- `Shift` / `Shift-R` — Z up/down
- `Ctrl-R` / `Ctrl-L` — open/close gripper
- `ESC` — quit
