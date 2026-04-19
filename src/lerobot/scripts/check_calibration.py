from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig

robot = SO100Follower(SO100FollowerConfig(port="/dev/tty.usbmodem58FA0817631", id="my_follower"))
robot.connect()
robot.bus.disable_torque()  # go limp so you can move by hand

print("Move joints by hand. Watch positions. Ctrl-C to stop.\n")
try:
    while True:
        obs = robot.bus.sync_read("Present_Position")
        print("\033[6A" if True else "", end="")  # move cursor up
        for motor, val in obs.items():
            print(f"{motor:<15} {val:+8.1f}°")
        import time; time.sleep(0.1)
except KeyboardInterrupt:
    pass

robot.bus.enable_torque()
robot.disconnect()