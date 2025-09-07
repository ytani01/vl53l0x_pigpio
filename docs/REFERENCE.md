# リファレンス

このドキュメントは `vl53l0x_pigpio` ライブラリとコマンドラインインターフェース(CLI)のAPIリファレンスです。

---

## ◆ `VL53L0X` クラス API

このクラスはVL53L0Xセンサーを制御するための主要なインターフェースです。

### === インポート

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
```

### === コンストラクタ

#### `VL53L0X(pi, i2c_bus=1, i2c_address=0x29, debug=False, config_file_path=None)`

センサーを初期化します。

-   **`pi`** (`pigpio.pi`): `pigpio`ライブラリの接続インスタンス。
-   **`i2c_bus`** (`int`, optional): I2Cバス番号。デフォルトは `1`。
-   **`i2c_address`** (`int`, optional): センサーのI2Cアドレス。デフォルトは `0x29`。
-   **`debug`** (`bool`, optional): デバッグログを有効にするか。デフォルトは `False`。
-   **`config_file_path`** (`pathlib.Path | None`, optional): オフセット値を読み込むための設定ファイルパス。

コンテキストマネージャ (`with`文) としても使用でき、終了時に自動的に`close()`を呼び出します。

```python
pi = pigpio.pi()
if not pi.connected:
    raise Exception("pigpioに接続できません")

try:
    with VL53L0X(pi) as sensor:
        # センサーを使用
        distance = sensor.get_range()
finally:
    pi.stop()
```

### === メソッド

#### `get_range() -> int`

> 単一の測距測定を実行します。

-   **戻り値**: 測定された距離 (mm)。オフセットが適用されます。

#### `get_ranges(num_samples: int) -> numpy.ndarray`

> 複数回の測距測定を連続して実行します。

-   **`num_samples`** (`int`): 測定回数。

-   **戻り値**: 測定結果のNumpy配列 (mm)。

#### `set_offset(offset_mm: int)`

> 測定値に適用するオフセット値を設定します。

-   **`offset_mm`** (`int`): オフセット値 (mm)。

#### `calibrate(target_distance_mm: int, num_samples: int) -> int`

> 既知の距離にあるターゲットを使用して、
センサーのオフセット値を校正します。

-   **`target_distance_mm`** (`int`): ターゲットまでの実際の距離 (mm)。
-   **`num_samples`** (`int`): 平均化のための測定回数。

-   **戻り値**: 計算されたオフセット値 (mm)。

#### `close()`

> I2C接続を閉じます。
コンテキストマネージャ(with)を使用している場合は自動的に呼び出されます。

---

## ◆ コマンドラインインターフェース (CLI)

`vl53l0x_pigpio` は、ターミナルからセンサーを操作するためのCLIを提供します。

### === グローバルオプション

すべてのサブコマンドで共通して使用できるオプションです。

-   `-C, --config-file TEXT`: 設定ファイルのパス (デフォルト: `(ホームディレクトリ)/vl53l0x.json`)
-   `-d, --debug`: デバッグモードを有効にします。
-   `-V, -v, --version`: バージョン情報を表示して終了します。
-   `-h, --help`: ヘルプメッセージを表示して終了します。

### === サブコマンド

#### `get`

> 距離を測定します。

> **使用法:** `vl53l0x_pigpio get [OPTIONS]`

> -   **`-c, --count INTEGER`**: 測定回数 (デフォルト: 10)
> -   **`-i, --interval FLOAT`**: 測定間隔（秒） (デフォルト: 1.0)

#### `performance`

> センサーの測定パフォーマンス（1秒あたりの測定回数など）を評価します。

> **使用法:** `vl53l0x_pigpio performance [OPTIONS]`

> -   **`-c, --count INTEGER`**: パフォーマンス評価のための測定回数 (デフォルト: 100)

#### `calibrate`

> センサーのオフセット値を校正し、設定ファイルに保存します。

> **使用法:** `vl53l0x_pigpio calibrate [OPTIONS]`

> -   **`-D, --distance INTEGER`**: ターゲットまでの実際の距離 (mm) (デフォルト: 100)
> -   **`-c, --count INTEGER`**: 平均化のための測定回数 (デフォルト: 10)
> -   **`-o, --output-file TEXT`**: 計算されたオフセットを保存するファイルパス (デフォルト: 設定ファイルと同じパス)
