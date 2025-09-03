#!/usr/bin/env python

import time
import pigpio
from vl53l0x_pigpio.driver import VL53L0X


def main(count=10):
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpio not connected.")
        return

    try:
        tof = VL53L0X(pi)
        for _ in range(count):
            distance = tof.get_range()
            if distance > 0:
                print(f"Distance: {distance} mm")
            time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if "tof" in locals() and tof:
            tof.close()
        pi.stop()


if __name__ == "__main__":
    main()
