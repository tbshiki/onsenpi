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
- 統合されたロギング機能
- 標準化された例外処理
- 型ヒント（Type Hints）による開発支援

## 使い方

### 初期化

```python
import logging
from sp_api.base import Marketplaces
from onsenpi import OnsenpiSPAPIClient

# クライアントの初期化（ロギングレベルの設定も可能）
client = OnsenpiSPAPIClient(
    marketplace=Marketplaces.JP,
    refresh_token='YOUR_REFRESH_TOKEN',
    lwa_app_id='YOUR_LWA_APP_ID',
    lwa_client_secret='YOUR_LWA_CLIENT_SECRET',
    log_level=logging.INFO  # ロギングレベルをカスタマイズ可能
)
```

### 例外処理

onsenpiは標準化された例外処理を提供しています。例外を適切に処理することで、より堅牢なアプリケーションを構築できます。

```python
from onsenpi import OnsenpiAPIError, OnsenpiException

try:
    # 2023年1月1日以降に作成された注文を取得
    orders = client.get_orders(create_after='2023-01-01')
    print(f"取得した注文数: {len(orders['Orders'])}")
except OnsenpiAPIError as e:
    print(f"API呼び出しエラー: {e}")
    print(f"元のエラー: {e.original_exception}")
except OnsenpiException as e:
    print(f"その他のエラー: {e}")
```

### ロギング設定のカスタマイズ

```python
import logging

# ロガーの取得とカスタマイズ
logger = logging.getLogger("onsenpi")
logger.setLevel(logging.DEBUG)  # より詳細なログを出力

# ファイルへのログ出力設定
file_handler = logging.FileHandler("onsenpi.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
```

### 注文情報の取得

```python
# 2023年1月1日以降に作成された注文を取得
orders = client.get_orders(create_after='2023-01-01')
if orders and 'Orders' in orders:
    print(f"取得した注文数: {len(orders['Orders'])}")
```

### 在庫情報のレポートリクエスト

```python
# 出品レポートをリクエスト
report_id = client.inventory.request_listing_report()
print(f"レポートID: {report_id}")

# レポートが準備できるまで待機
document_id = client.inventory.wait_for_report_to_be_ready(report_id)
if document_id:
    print(f"ドキュメントID: {document_id}")

    # レポートをダウンロード
    success = client.inventory.download_report_data(document_id, "temp_report.gz")
    if success:
        # GZIPからTXTへ変換
        from onsenpi import DataConverter
        DataConverter.convert_gzip_to_txt(
            "temp_report.gz",
            "listing_report.txt",
            delete_original=True
        )
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
