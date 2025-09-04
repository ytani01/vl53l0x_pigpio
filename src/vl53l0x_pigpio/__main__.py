#
# (c) 2025 Yoichi Tanibayashi
#
import time

import click
import pigpio

from . import __version__, get_logger, VL53L0X

log = get_logger(__name__)

_name = __name__

@click.group(
    invoke_without_command=True,
    help="""
VL53L0X driver CLI
"""
)
@click.option("--debug", "-d", is_flag=True, help="debug flag")
@click.version_option(
    __version__, "--version", "-v", "-V", message='%(prog)s %(version)s'
)
@click.help_option("--help", "-h")
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """VL53L0X距離センサーのPythonドライバー用CLIツール。"""
    cmd_name = ctx.info_name
    subcmd_name = ctx.invoked_subcommand

    __log = get_logger(str(cmd_name), debug)

    __log.debug("cmd_name=%a, subcmd_name=%a", cmd_name, subcmd_name)
    
    if subcmd_name is None:
        print(f"{ctx.get_help()}")


@cli.command(
    help="""
get distance"""
)
@click.option(
    "--count", "-c", type=int, default=10, show_default=True, help="count"
)
@click.option(
    "--interval", "-i", type=float, default=1.0, show_default=True,
    help="interval seconds"
)
@click.option("--debug", "-d", is_flag=True, default=False, help="debug flag")
@click.version_option(
    __version__, "--version", "-v", "-V", message='%(prog)s %(version)s'
)
@click.help_option("--help", "-h")
@click.pass_context
def get(ctx, count, interval, debug):
    """基本的な例を実行します。"""
    __log = get_logger(__name__, debug)
    __log.debug("count=%s, interval=%s", count, interval)

    cmd_name = ctx.command.name
    __log.debug("cmd_name=%a", cmd_name)
    
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("cannnto connect pigpiod")

    try:
        with VL53L0X(pi, debug=debug) as sensor:
            for i in range(count):
                distance: int = sensor.get_range()
                if distance > 0:
                    click.echo(f"{i + 1}/{count}: {distance} mm")
                else:
                    click.echo(f"{i + 1}/{count}: 無効なデータ。")
                time.sleep(interval)
    finally:
        pi.stop()


@cli.command()
@click.option(
    "--count", type=int, default=100, show_default=True, help="count"
)
@click.option("--debug", "-d", is_flag=True, default=False, help="debug flag")
@click.version_option(
    __version__, "--version", "-v", "-V", message='%(prog)s %(version)s'
)
@click.help_option("--help", "-h")
@click.pass_context
def performance(ctx, count, debug):
    """VL53L0Xセンサーの測定パフォーマンスを評価します。"""
    __log = get_logger(__name__, debug)
    __log.debug("count=%s", count)

    cmd_name = ctx.command.name
    __log.debug("cmd_name=%a", cmd_name)
    
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("cannnto connect pigpiod")

    try:
        with VL53L0X(pi, debug=debug) as sensor:
            click.echo(f"{count}回の距離測定パフォーマンスを評価します...")
            start_time = time.perf_counter()
            for _ in range(count):
                sensor.get_range()
            end_time = time.perf_counter()

            total_time = end_time - start_time
            avg_time_per_measurement = total_time / count
            measurements_per_second = count / total_time

            click.echo("---")
            click.echo(f"合計時間: {total_time:.4f} 秒")
            click.echo(f"1回あたりの平均時間: {avg_time_per_measurement * 1000:.4f} ms")
            click.echo(f"1秒あたりの測定回数: {measurements_per_second:.2f} 回/秒")
            click.echo("---")
    finally:
        pi.stop()
