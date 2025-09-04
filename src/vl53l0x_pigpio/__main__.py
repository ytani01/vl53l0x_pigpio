import click
import time
import pigpio
import numpy as np
from vl53l0x_pigpio.driver import VL53L0X
from importlib.metadata import version, PackageNotFoundError
from .my_logger import get_logger

# ロガーのセットアップ
log = get_logger(__name__)

try:
    __version__ = version("vl53l0x_pigpio")
except PackageNotFoundError:
    __version__ = "unknown"

class SensorContext:
    """
    VL53L0Xセンサーとpigpio接続を管理するためのコンテキストクラス。
    """

    def __init__(self, debug=False):
        self.pi = None
        self.tof = None
        self.debug = debug
        # デバッグモードに応じてロガーを再設定
        if self.debug:
            log.setLevel("DEBUG")
        else:
            log.setLevel("INFO")

    def __enter__(self):
        log.debug("デバッグモード: pigpioに接続します...")
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise click.ClickException(
                "pigpioデーモンに接続できませんでした。実行中であることを確認してください。"
            )
        log.debug("デバッグモード: VL53L0Xを初期化します...")
        self.tof = VL53L0X(self.pi, debug=self.debug)
        return self.tof

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tof:
            log.debug("デバッグモード: I2C接続を閉じます...")
            self.tof.close()
        if self.pi:
            log.debug("デバッグモード: pigpio接続を停止します...")
            self.pi.stop()

@click.group()
@click.version_option(version=__version__, prog_name="vl53l0x_pigpio")
@click.option('--debug', is_flag=True, help='デバッグモードを有効にします。')
@click.pass_context
def main(ctx, debug):
    """VL53L0X距離センサーのPythonドライバー用CLIツール。"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    if debug:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")

@main.command()
@click.option("--count", default=10, help="取得する距離データの数。")
@click.pass_context
def example(ctx, count):
    """基本的な例を実行します。"""
    debug = ctx.obj['DEBUG']
    with SensorContext(debug=debug) as sensor:
        click.echo(f"{count}回の距離測定を開始します...")
        for i in range(count):
            distance = sensor.get_range()
            if distance > 0:
                click.echo(f"測定 {i + 1}: {distance} mm")
            else:
                click.echo(f"測定 {i + 1}: 無効なデータ。")
            time.sleep(0.1)

@main.command()
@click.argument("samples", type=int, default=100)
@click.pass_context
def numpy_example(ctx, samples):
    """複数の距離データを取得し、統計情報を表示します。"""
    debug = ctx.obj['DEBUG']
    with SensorContext(debug=debug) as sensor:
        click.echo(f"{samples}個のサンプルを取得しています...")
        ranges = sensor.get_ranges(samples)
        click.echo("---")
        click.echo(f"平均:   {np.mean(ranges):.2f} mm")
        click.echo(f"標準偏差: {np.std(ranges):.2f} mm")
        click.echo(f"最小値:    {np.min(ranges)} mm")
        click.echo(f"最大値:    {np.max(ranges)} mm")
        click.echo("---")