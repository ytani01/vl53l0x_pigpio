# ToDo.md

## 優先項目
- [x] `GEMINI.md`を精読。ルールを守ることを徹底する。
- [x] `samples`以下のサンプルプログラムの再確認。
- [x] `README.md`を再確認して、必要に応じて修正。
- [x] 自動テストプログラムの作成
- [x] 自動テストの実行
    - `uv run python -m pytest -v ....`を使うこと。
- [x] すべてのソースコードと全体的なリファクタリング
    - **注意**: `my_logger.py` は、変更してはならない。
- [x] リファクタリング後の自動テストの実行
    - `uv run python -m pytest -v ....`を使うこと。
- [ ] ここまでできたら、ユーザーに報告して指示を待つ。


## 余裕があればやること: 実行する前に、ユーザーに確認すること
- [ ] `get_measurement_timing_budget`と`set_measurement_timing_budget`を実装する。 (要追加調査/外部API参照)
  - 参考情報URL: [Pololu社:Arduino用 C++ ソースコード](https://github.com/pololu/vl53l0x-arduino)
