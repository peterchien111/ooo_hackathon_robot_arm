# SO-100 Robot Arm — OOO Hackathon

## Hardware
- SO-100 follower arm (no leader arm)
- Connected via USB to your computer

---

## Installation

Follow the [official LeRobot installation guide](https://huggingface.co/docs/lerobot/installation?create_venv=uv+%28PyTorch+%3E%3D+2.10+only%29) using the **uv** route. Summary:

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone this repo
```bash
git clone https://github.com/peterchien111/ooo_hackathon_robot_arm.git
cd ooo_hackathon_robot_arm
```

### 3. Create a virtual environment
```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 4. Install ffmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 5. Install dependencies
```bash
uv pip install -e ".[core_scripts,feetech]"
```

---

## Robot Setup (first time only)

### 1. Find your USB port
Plug in the robot and run:
```bash
uv run lerobot-find-port
```
Note the port (e.g. `/dev/tty.usbmodem585A0076841` on Mac, `/dev/ttyACM0` on Linux).

> **Linux only:** you may need to run `sudo chmod 666 /dev/ttyACM0` first.

### 2. Set motor IDs (already done, skip this)
Connect each motor **one at a time** to the controller board:
```bash
uv run lerobot-setup-motors \
    --robot.type=so100_follower \
    --robot.port=YOUR_PORT_HERE
```

### 3. Load the shared calibration
Copy the calibration file from this repo to the right location:
```bash
mkdir -p ~/.cache/huggingface/lerobot/calibration/robots/so_follower/
cp calibration.json ~/.cache/huggingface/lerobot/calibration/robots/so_follower/my_follower.json
```

> If the shared calibration doesn't work well on your unit, re-calibrate:
> ```bash
> uv run lerobot-calibrate \
>     --robot.type=so100_follower \
>     --robot.port=YOUR_PORT_HERE \
>     --robot.id=my_follower
> ```
> - Move arm to middle of its range → press Enter
> - Move each joint through its full range → press Enter

---

## Usage

Update `PORT` at the top of each script to match your port before running.

### Move to preset positions
```bash
uv run python move.py
```

| Command | Action |
|---------|--------|
| `A` | Move to position A at default speed |
| `B 3` | Move to position B at speed 3 (1=slow, 10=fast) |
| `list` | Show all positions + current joint values |
| `q` | Quit |

To add your own positions, edit the `POSITIONS` dict in `move.py`. Run `list` to see current joint values to copy.

### Keyboard teleoperation (i don't think this works yet but don't really need this)
```bash
uv run python keyboard_teleop.py
```

| Key | Action |
|-----|--------|
| `↑ ↓ ← →` | Move end-effector X/Y |
| `Shift` / `Shift-R` | Move up / down (Z) |
| `Ctrl-R` | Open gripper |
| `Ctrl-L` | Close gripper |
| `ESC` | Quit |
