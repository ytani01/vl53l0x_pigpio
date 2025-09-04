# ToDo.md

## 優先項目
- [x] `__main__.py` と `cli.py`を統合する。
- [x] デバッグログでは、`my_logger.py` の `get_logger`を使う
    - **注意**: `my_logger.py` は、変更してはならない。
- [x] `SensorContext`クラスを  `VL53L0X`クラスに統合する。
        つまり、 `with VL53L0X(pi) as sensor:`という使い方ができるようにする。
- [x] CLIのオプションとして、以下の実装は必須: **省略形オプションも**必ず実装する
    - [x] ヘルプ表示: '-h'と'--help'
    - [x] デバッグフラグ: '-d'と'--debug'
    - [x] バージョン表示: '-v'と'--version': 
- [x] すべてのソースコードと全体的なリファクタリング
- [x] ここまでできたら、ユーザーに報告して指示を待つ。


## 余裕があればやること: 実行する前に、ユーザーに確認すること
- [ ] `get_measurement_timing_budget`と`set_measurement_timing_budget`を実装する。 (要追加調査/外部API参照)
  - 参考情報URL: [Pololu社:Arduino用 C++ ソースコード](https://github.com/pololu/vl53l0x-arduino)
