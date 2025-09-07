# PyPIへの公開方法

このドキュメントでは、`vl53l0x_pigpio` パッケージを TestPyPI と PyPI に公開する手順を説明します。

## 1. ビルド

まず、配布用のパッケージをビルドします。以下のコマンドを実行すると、`dist/` ディレクトリにパッケージファイルが作成されます。

```bash
uv build
```

---

## 2. 認証情報の設定（推奨）

毎回アップロードのたびにユーザー名とパスワードを入力する代わりに、ファイルに認証情報を保存しておくと、コマンド実行だけでアップロードが完了して便利です。

**重要**: `pyproject.toml` のようなバージョン管理されるファイルには、APIトークンなどの機密情報を絶対に書き込まないでください。

### 方法1: `hatch` の設定ファイルを利用する（推奨）

`hatch`のコマンドを使って、認証情報を安全な場所に保存する方法です。

以下のコマンドを実行して、TestPyPIとPyPIの認証情報をそれぞれ設定します。`<...>`の部分はご自身のAPIトークンに置き換えてください。

**TestPyPI用:**
```bash
hatch config set publish.test.user __token__
hatch config set publish.test.auth '<your-testpypi-token>'
```

**本番PyPI用:**
```bash
hatch config set publish.pypi.user __token__
hatch config set publish.pypi.auth '<your-pypi-token>'
```

### 方法2: `.pypirc` ファイルを利用する（従来の方法）

ホームディレクトリ (`~`) に `.pypirc` ファイルを作成し、認証情報を記述する方法です。

**ファイル:** `~/.pypirc`
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-token>
```

---

## 3. TestPyPIへの公開 (テスト用)

### 3.1. アカウントとAPIトークンの準備

1.  [TestPyPI](https://test.pypi.org/) でアカウントを作成します。
2.  ログイン後、[API tokens](https://test.pypi.org/manage/account/token/) のページでAPIトークンを生成します。
    -   **Scope**: `Project: vl53l0x_pigpio` に限定することを推奨します。
    -   生成されたトークン (`pypi-` から始まる文字列) は一度しか表示されないため、必ずコピーしてください。

**プロジェクト初回公開時の注意:**

PyPI/TestPyPIにまだプロジェクトが存在しない場合、プロジェクトにスコープを限定したAPIトークンは作成できません。その場合、初回のみ以下の手順が必要です。

1.  スコープを **`Entire account (all projects)`** に設定した一時的なトークンを作成して、初回アップロードを行います。
2.  アップロード成功後、プロジェクトに限定した正式なトークンを再作成します。
3.  セキュリティのため、最初に使用した一時的なトークンは削除します。

### 3.2. アップロード

以下のコマンドを実行して、TestPyPIにパッケージをアップロードします。

```bash
uv run hatch publish -r test
```

「2. 認証情報の設定」を行っていない場合は、コマンド実行後にユーザー名とパスワードの入力を求められます。

-   **ユーザー名**: `__token__`
-   **パスワード**: 3.1で取得したAPIトークン

アップロード後、`https://test.pypi.org/project/vl53l0x_pigpio/` でパッケージが公開されていることを確認できます。

---

## 4. PyPIへの公開 (本番)

### 4.1. アカウントとAPIトークンの準備

1.  [PyPI](https://pypi.org/) でアカウントを作成します。(TestPyPIとは別のアカウントです)
2.  ログイン後、[API tokens](https://pypi.org/manage/account/token/) のページでAPIトークンを生成します。
    -   **Scope**: `Project: vl53l0x_pigpio` に限定することを推奨します。（初回公開時は上記注意参照）
    -   生成されたトークンをコピーします。

### 4.2. アップロード

以下のコマンドを実行して、PyPIにパッケージをアップロードします。

```bash
uv run hatch publish
```

「2. 認証情報の設定」を行っていない場合は、同様に認証情報の入力が求められます。

アップロード後、`https://pypi.org/project/vl53l0x_pigpio/` でパッケージが公開されていることを確認できます。
