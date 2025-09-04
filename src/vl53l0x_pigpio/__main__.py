import click
import time
import pigpio
import numpy as np
from vl53l0x_pigpio import VL53L0X


class SensorContext:
    """
    VL53L0Xセンサーとpigpio接続を管理するためのコンテキストクラス。
    """

    def __init__(self):
        self.pi = None
        self.tof = None

    def __enter__(self):
        self.pi = pigpio.pi()  # pigpioデーモンに接続
        if not self.pi.connected:
            raise click.ClickException(
                "pigpioデーモンに接続できませんでした。実行中であることを確認してください。"
            )
        self.tof = VL53L0X(self.pi)  # VL53L0Xセンサーを初期化
        return self.tof

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tof:
            self.tof.close()  # センサーオブジェクトが存在する場合、I2C接続を閉じます
        if self.pi:
            self.pi.stop()  # pigpio接続を停止


@click.group()
def main():
    """VL53L0X距離センサーのPythonドライバー用CLIツール。

    このツールは、VL53L0Xセンサーとの対話のためのコマンドを提供します。
    例えば、距離の単一測定や、複数のサンプルからの統計情報の取得などです。
    """
    pass


@main.command()
@click.option("--count", default=10, help="取得する距離データの数。")
def example(count):
    """
    VL53L0Xセンサーから距離データを取得する基本的な例を実行します。

    指定された回数だけ距離測定を行い、結果をミリメートル単位で表示します。
    pigpioデーモンが実行されている必要があります。
    """
    with SensorContext() as sensor:  # SensorContextを直接使用
        click.echo(f"{count}回の距離測定を開始します...")
        for i in range(count):
            distance = sensor.get_range()  # 距離測定を実行
            if distance > 0:
                click.echo(f"測定 {i + 1}: {distance} mm")
            else:
                click.echo(f"測定 {i + 1}: 無効な距離データを受信しました。")
            time.sleep(0.1)  # 測定間の短い遅延


@main.command()
@click.argument("samples", type=int, default=100)
def numpy_example(samples):
    """
    VL53L0Xセンサーから複数の距離データを取得し、統計情報を表示します。

    指定された数のサンプルを取得し、平均、標準偏差、最小値、最大値を計算して表示します。
    pigpioデーモンが実行されている必要があります。
    """
    with SensorContext() as sensor:  # SensorContextを直接使用
        click.echo(f"{samples}個のサンプルを取得しています...")
        ranges = sensor.get_ranges(samples)  # 複数の距離測定を実行

        click.echo("---")
        click.echo(f"平均:   {np.mean(ranges):.2f} mm")
        click.echo(f"標準偏差: {np.std(ranges):.2f} mm")
        click.echo(f"最小値:    {np.min(ranges)} mm")
        click.echo(f"最大値:    {np.max(ranges)} mm")
        click.echo("---")