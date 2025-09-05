#
# (c) 2025 Yoichi Tanibayashi
#
"""キャリブレーション機能のサンプルコード"""
import click
import pigpio
from vl53l0x_pigpio import VL53L0X

@click.command()
@click.option("--distance", "-d", type=int, default=100, show_default=True, help="distance to target [mm]")
@click.option("--count", "-c", type=int, default=10, show_default=True, help="count")
@click.option("--debug", is_flag=True, default=False, help="debug flag")
def main(distance: int, count: int, debug: bool) -> None:
    

    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("cannot connect to pigpiod")

    try:
        with VL53L0X(pi, debug=debug) as sensor:
            click.echo(f"{distance}mmの距離にターゲットを置いてください。")
            click.echo("準備ができたらEnterキーを押してください...")
            input()

            offset = sensor.calibrate(distance, count)
            click.echo(f"計算されたオフセット値: {offset} mm")

            click.echo("オフセット値をセンサーに設定します。")
            sensor.set_offset(offset)

            click.echo("オフセット適用後の距離を測定します...")
            measured_distance = sensor.get_range()
            click.echo(f"補正後の測定距離: {measured_distance} mm")

    finally:
        pi.stop()

if __name__ == "__main__":
    main()
