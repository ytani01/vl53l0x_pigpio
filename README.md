# VL53L0X pigpio

## 概要

VL53L0X 距離センサーを制御するための Python ドライバーです。

## 特徴

- `pigpio` ライブラリを利用し、全てPythonで実装
- Raspberry Pi Zero 2W など、低スペックの機種でも実行可能


## インストール

```bash
pip install vl53l0x-pigpio
```


## 使い方

```python
import pigpio
from vl53l0x_pigpio.driver import VL53L0X

# pigpio に接続
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio に接続できません")

# VL53L0X センサーを初期化し、with ステートメントで確実にクリーンアップ
with VL53L0X(pi) as tof:
    try:
        # 距離を測定
        distance = tof.get_range()
        print(f"距離: {distance} mm")
    finally:
        # pigpio のリソースを解放
        pi.stop()

```
