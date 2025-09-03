"""
An example of using the VL53L0X driver with numpy.
"""

import click
import pigpio
import numpy as np
from vl53l0x_pigpio.driver import VL53L0X


@click.command()
@click.argument("samples", type=int, default=100)
def main(samples):
    """
    Main function
    """
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("Could not connect to pigpio.")

    tof = VL53L0X(pi)

    try:
        print(f"Getting {samples} samples...")
        # Get 100 samples
        ranges = tof.get_ranges(samples)

        print("---")
        print(f"Mean:   {np.mean(ranges):.2f} mm")
        print(f"Std dev: {np.std(ranges):.2f} mm")
        print(f"Min:    {np.min(ranges)} mm")
        print(f"Max:    {np.max(ranges)} mm")
        print("---")

    finally:
        tof.close()
        pi.stop()


if __name__ == "__main__":
    main()
