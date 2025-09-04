import time

import click
from click import Parameter
import numpy as np
import pigpio

from typing import Any

from importlib.metadata import PackageNotFoundError, version

from vl53l0x_pigpio.driver import VL53L0X

from .my_logger import get_logger

# ロガーのセットアップ
log = get_logger(__name__)

try:
    __version__ = version("vl53l0x_pigpio")
except PackageNotFoundError:
    __version__ = "unknown"

def print_version_and_exit(ctx: click.Context, param: click.Option | Parameter, value: bool) -> Any:
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"vl53l0x_pigpio, version {__version__}")
    ctx.exit()

@click.group()
@click.option('-v', '--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version_and_exit, help='バージョンを表示して終了します。')
@click.option('-d', '--debug', is_flag=True, help='デバッグモードを有効にします。')
@click.pass_context
def main(ctx: click.Context, debug: bool):
    """VL53L0X距離センサーのPythonドライバー用CLIツール。"""
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    if debug:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")

@main.command()
@click.option("--count", default=10, help="取得する距離データの数。")
@click.pass_context
def example(ctx: click.Context, count: int):
    """基本的な例を実行します。"""
    debug: bool = ctx.obj["DEBUG"]
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException(
            "pigpioデーモンに接続できませんでした。実行中であることを確認してください。"
        )
    try:
        with VL53L0X(pi, debug=debug) as sensor:
            click.echo(f"{count}回の距離測定を開始します...")
            for i in range(count):
                distance: int = sensor.get_range()
                if distance > 0:
                    click.echo(f"測定 {i + 1}: {distance} mm")
                else:
                    click.echo(f"測定 {i + 1}: 無効なデータ。")
                time.sleep(0.1)
    finally:
        pi.stop()

@main.command()
@click.argument("samples", type=int, default=100)
@click.pass_context
def numpy_example(ctx: click.Context, samples: int):
    """複数の距離データを取得し、統計情報を表示します。"""
    debug: bool = ctx.obj["DEBUG"]
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException(
            "pigpioデーモンに接続できませんでした。実行中であることを確認してください。"
        )
    try:
        with VL53L0X(pi, debug=debug) as sensor:
            click.echo(f"{samples}個のサンプルを取得しています...")
            ranges: np.ndarray = sensor.get_ranges(samples)
            click.echo("---")
            click.echo(f"平均:   {np.mean(ranges):.2f} mm")
            click.echo(f"標準偏差: {np.std(ranges):.2f} mm")
            click.echo(f"最小値:    {np.min(ranges)} mm")
            click.echo(f"最大値:    {np.max(ranges)} mm")
            click.echo("---")
    finally:
        pi.stop()