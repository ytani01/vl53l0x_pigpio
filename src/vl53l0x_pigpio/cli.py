import click
import time
import pigpio
import numpy as np
from vl53l0x_pigpio import VL53L0X

@click.group()
def main():
    """VL53L0X pigpio CLI tool."""
    pass

@main.command()
@click.option('--count', default=10, help='Number of readings.')
def example(count):
    """Run the example to get distance readings."""
    pi = pigpio.pi()
    if not pi.connected:
        click.echo("pigpio not connected.")
        return

    try:
        tof = VL53L0X(pi)
        for _ in range(count):
            distance = tof.get_range()
            if distance > 0:
                click.echo(f"Distance: {distance} mm")
            time.sleep(0.1)
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        if 'tof' in locals() and tof:
            tof.close()
        pi.stop()

@main.command()
@click.argument("samples", type=int, default=100)
def numpy_example(samples):
    """Run the numpy example to get distance readings and statistics."""
    pi = pigpio.pi()
    if not pi.connected:
        click.echo("Could not connect to pigpio.")
        return

    tof = VL53L0X(pi)

    try:
        click.echo(f"Getting {samples} samples...")
        ranges = tof.get_ranges(samples)

        click.echo("---")
        click.echo(f"Mean:   {np.mean(ranges):.2f} mm")
        click.echo(f"Std dev: {np.std(ranges):.2f} mm")
        click.echo(f"Min:    {np.min(ranges)} mm")
        click.echo(f"Max:    {np.max(ranges)} mm")
        click.echo("---")

    finally:
        tof.close()
        pi.stop()