# onsenpi

温泉（Onsen）のように、Amazon SP-APIを使いやすく、快適にするPythonラッパーライブラリ。

SP-API -> spapi -> spa + pi -> onsen + pi -> onsenpi

## 概要

onsenpiは開発者向けにAmazon Selling Partner API（SP-API）の使用を簡素化するライブラリです。
このライブラリはAPIとの対話をより直感的で扱いやすくすることで、開発効率を高めます。

## インストール方法

```bash
pip install onsenpi
```

## 主な機能

- シンプルで直感的なインターフェース
- 複雑なSP-API呼び出しの抽象化
- データ変換機能の提供
- 在庫、注文、商品情報の簡単な取得

## 使い方

### 初期化

```python
from onsenpi import OnsenpiSPAPIClient

# 認証情報の設定
credentials = {
    'refresh_token': 'YOUR_REFRESH_TOKEN',
    'lwa_app_id': 'YOUR_LWA_APP_ID',
    'lwa_client_secret': 'YOUR_LWA_CLIENT_SECRET',
    'aws_access_key': 'YOUR_AWS_ACCESS_KEY',
    'aws_secret_key': 'YOUR_AWS_SECRET_KEY',
    'role_arn': 'YOUR_ROLE_ARN'
}

# クライアントの初期化
client = OnsenpiSPAPIClient(credentials, marketplace='JP')
```

### 注文情報の取得

```python
# 2023年1月1日以降に作成された注文を取得
orders = client.get_orders(created_after='2023-01-01')
print(f"取得した注文数: {len(orders)}")
```

### 在庫情報の取得

```python
# 在庫情報の取得
inventory = client.get_inventory()
print(f"在庫アイテム数: {len(inventory)}")
```

### 商品情報の取得

```python
# ASINから商品情報を取得
asin = 'EXAMPLE_ASIN'
product = client.get_product_by_asin(asin)
print(f"商品情報: {product}")
```

より詳細な使用例は[examples](./examples)ディレクトリをご覧ください。

## 開発環境のセットアップ

開発に参加される方は、以下の手順で環境をセットアップしてください：

```bash
# リポジトリのクローン
git clone https://github.com/tbshiki/onsenpi.git
cd onsenpi

# 開発用依存パッケージのインストール
pip install -e ".[dev]"

# テストの実行
pytest

# コードフォーマット
black .
isort .

# リント
flake8
```

## 参考リンク

- [Amazon SP-API 開発者ドキュメント](https://developer-docs.amazon.com/sp-api/)
- [Python Amazon SP-API ドキュメント](https://python-amazon-sp-api.readthedocs.io/)
