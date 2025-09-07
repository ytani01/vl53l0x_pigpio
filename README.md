# VL53L0X pigpio

## ◆ 概要

`pigpio`ライブラリを使用してVL53L0X距離センサーを制御するためのPythonドライバーです。
Raspberry Pi OSでの使用を前提としています。

## ◆ 特徴

- `pigpio` を利用し、すべてPythonで実装
- ライブラリとして、またCLIツールとして利用可能
- オフセットキャリブレーション機能

## ◆ インストール

このパッケージは、Raspberry Pi OSでの使用を前提としています。

### === 仮想環境の作成

パッケージをクリーンな環境にインストールするため、仮想環境を作成することを強く推奨します。

```bash
# プロジェクト用のディレクトリを作成し、移動
mkdir my_sensor_project
cd my_sensor_project

# 仮想環境を作成
python -m venv .venv

# 仮想環境を有効化 (Linux / macOS)
source .venv/bin/activate
```

### === パッケージのインストール

以下のコマンドで、TestPyPIからパッケージをインストールします。

```bash
pip install -U \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  vl53l0x_pigpio
```
*(注: このパッケージは現在TestPyPIで公開されています。将来、本番のPyPIに公開された際は、インストールコマンドが `pip install vl53l0x_pigpio` に変更される予定です。)*

## ◆ ライブラリとしての使い方

基本的な使い方は以下の通りです。

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

# pigpioに接続
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpioに接続できません")

try:
    # withステートメントでセンサーを初期化
    # 自動的に設定ファイル(~/vl53l0x.json)が読み込まれます
    with VL53L0X(pi) as tof:
        # 距離を測定
        distance = tof.get_range()
        if distance > 0:
            print(f"距離: {distance} mm")
        else:
            print("無効なデータ。")

finally:
    # pigpioのリソースを解放
    pi.stop()
```

## ◆ CLIツールの使い方

仮想環境を有効にすると、`vl53l0x_pigpio`コマンドが使用できます。

### === ヘルプ

```bash
vl53l0x_pigpio --help
```

### === 距離の測定 (`get`)

```bash
vl53l0x_pigpio get --count 5
```

### === パフォーマンス測定 (`performance`)

```bash
vl53l0x_pigpio performance --count 500
```

### === キャリブレーション (`calibrate`)

```bash
vl53l0x_pigpio calibrate --distance 150
```
*(各コマンドの詳細なオプションは `vl53l0x_pigpio [コマンド名] --help` で確認できます)*

より詳細なライブラリAPIやコマンドの仕様については、[docs/REFERENCE.md](docs/REFERENCE.md)を参照してください。

## ◆ 参考情報

- [Pololu社:Arduino用 C++ ソースコード](https://github.com/pololu/vl53l0x-arduino)
- https://github.com/cassou/VL53L0X_rasp
- https://github.com/johnbryanmoore/VL53L0X_rasp_python


## ◆ AIの活用

以下のAIと **協力しながら** 作成しました。
とはいえ、作らせっぱなしにするのではなく、
随時人間が確認し、相当な手を加えています。

- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [ChatGPT](https://chatgpt.com/)
- [claude](https://claude.ai/)


## ◆ ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。
