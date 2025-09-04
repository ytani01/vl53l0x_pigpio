# ToDo.md

## 優先項目
- [x] `__main__.py` と `cli.py`を統合する。
- [x] CLIのオプションとして、以下の実装は必須
    - [x] '-h', '--help': ヘルプ表示
    - [x] '-d', '--debug': デバッグ用フラグ
    - [x] '-v', '--version': バージョン表示
- [ ] デバッグログでは、`my_logger.py` の `get_logger`を使う
- [ ] すべてのソースコードと全体的なリファクタリング
- [ ] ここまでできたら、ユーザーに報告して指示を待つ。


## 余裕があればやること: 実行する前に、ユーザーに確認すること
- [ ] `get_measurement_timing_budget`と`set_measurement_timing_budget`を実装する。 (要追加調査/外部API参照)
  - 参考情報URL: [Pololu社:Arduino用 C++ ソースコード](https://github.com/pololu/vl53l0x-arduino)
