# Tasks

## 1. `from vl53l0x_pigpio import VL53L0X` 形式でのインポート対応

- [ ] `src/vl53l0x_pigpio/__init__.py` を編集し、`VL53L0X` クラスをトップレベルの名前空間にインポートする。具体的には、`from .driver import VL53L0X` のような行を追加する。
- [ ] 簡単なテストスクリプトを作成し、`from vl53l0x_pigpio import VL53L0X` で正しくインポートできることを確認する。

## 2. `click` を用いた CLI の実装

- [ ] `pyproject.toml` の `[project.dependencies]` に `click` を追加する。
- [ ] `src/vl53l0x_pigpio/cli.py` を新規作成し、`click` を使った基本的なコマンドグループを定義する。
- [ ] `samples/example.py` の内容を `cli.py` に `example` サブコマンドとして移植する。
- [ ] `samples/numpy_example.py` の内容を `cli.py` に `numpy_example` サブコマンドとして移植する。
- [ ] `pyproject.toml` に `[project.scripts]` を追加し、`vl53l0x-cli = "vl53l0x_pigpio.cli:main"` のようにコマンドのエントリーポイントを設定する。
- [ ] `uv run vl53l0x-cli --help` を実行し、サブコマンドが表示されることを確認する。
- [ ] `uv run vl53l0x-cli example` と `uv run vl53l0x-cli numpy-example` を実行し、サンプルが正しく動作することを確認する。
