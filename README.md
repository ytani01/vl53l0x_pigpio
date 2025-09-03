# VL53L0X pigpio

## 概要

Raspberry Pi Zero 2W と pigpio を使用して、VL53L0X 距離センサーを制御するための Python ドライバーです。

## 特徴

-   `pigpio` ライブラリを利用した I2C 通信
-   `numpy` を活用した高速なデータ処理
-   シンプルな API

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

# センサーを初期化
tof = VL53L0X(pi)
tof.open()
tof.start_ranging()

try:
    # 距離を測定
    distance = tof.get_distance()
    print(f"距離: {distance} mm")

finally:
    # クリーンアップ
    tof.stop_ranging()
    tof.close()
    pi.stop()

```

## ライセンス

[MIT](./LICENSE)
