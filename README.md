# onsenpi

温泉（Onsen）のように、Amazon SP-APIを使いやすく、快適にするPythonラッパーライブラリ。

SP-API -> spapi -> spa + pi -> onsen + pi -> onsenpi

## 概要

onsenpiは開発者向けにAmazon Selling Partner API（SP-API）の使用を簡素化するライブラリです。
このライブラリはAPIとの対話をより直感的で扱いやすくすることで、開発効率を高めます。

## 最新情報（v0.2.3）

- 型ヒント（Type Hints）の完全実装によるコード補完とエラー検出の強化
- エラー処理の一貫性向上とより詳細なエラー情報の提供
- パフォーマンス最適化とリソース効率の改善
- 各モジュールの機能拡張とドキュメント強化
- コンテキストマネージャなどの便利な機能追加

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
- コンテキストマネージャによる安全なファイル操作

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
from onsenpi import OnsenpiAPIError, OnsenpiException, OnsenpiValidationError

try:
    # 過去30日間の注文を取得（日付指定がない場合は自動的に過去30日間）
    orders = client.get_orders()
    print(f"取得した注文数: {len(orders['Orders'])}")
except OnsenpiAPIError as e:
    print(f"API呼び出しエラー: {e}")
    print(f"エラー詳細: {e.get_error_details()}")
except OnsenpiValidationError as e:
    print(f"入力値検証エラー: {e}")
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
# 過去30日間の出荷待ち注文を取得
orders = client.get_orders(order_statuses=["Unshipped"])
if orders and 'Orders' in orders:
    print(f"取得した注文数: {len(orders['Orders'])}")

    # 最初の注文の詳細を取得
    if orders['Orders']:
        order_id = orders['Orders'][0]['AmazonOrderId']
        order_items = client.get_order_items(order_id)
        print(f"注文アイテム数: {len(order_items['OrderItems'])}")
```

### 在庫情報のレポートリクエスト

```python
# 出品レポートをリクエスト
report_response = client.inventory.request_listing_report()
report_id = report_response.get("reportId")
print(f"レポートID: {report_id}")

# レポートが準備できるまで待機
document_id = client.inventory.wait_for_report_to_be_ready(report_id)
if document_id:
    print(f"ドキュメントID: {document_id}")

    # レポートをダウンロード
    temp_gzip_file = "temp_report.gz"
    if client.inventory.download_report_data(document_id, temp_gzip_file):
        # ダウンロードしたGZIPファイルをテキストに変換
        from onsenpi import DataConverter
        DataConverter.convert_gzip_to_txt(temp_gzip_file, "report.txt", delete_original=True)
        print("レポートの変換が完了しました")
```

### 商品情報の検索

```python
# キーワードで商品カタログを検索
search_results = client.product.search_catalog_items("keyboard")
if search_results and "items" in search_results:
    print(f"検索結果: {len(search_results['items'])} 件")

    # 検索結果から最初のASINを取得
    if search_results['items']:
        asin = search_results['items'][0].get('asin')

        # 商品の詳細情報を取得
        item_details = client.product.get_item(asin)
        print(f"商品名: {item_details.get('attributes', {}).get('title', 'Unknown')}")
```

### ファイル操作の安全な実行

```python
from onsenpi import DataConverter

# コンテキストマネージャによる安全なファイル読み込み
try:
    with DataConverter.open_file_safely("report.txt", "r", encoding="cp932") as f:
        content = f.read()
        print(f"ファイルサイズ: {len(content)} バイト")
except Exception as e:
    print(f"ファイル操作エラー: {e}")
```

## 開発者向け情報

### 依存関係のインストール

```bash
# 開発用の依存関係をインストール
pip install -e ".[dev]"
```

### テスト実行

```bash
# テストを実行
pytest

# カバレッジレポート付きでテストを実行
pytest --cov=onsenpi
```

### コード品質チェック

```bash
# コードフォーマット
black onsenpi tests

# インポート順序の最適化
isort onsenpi tests

# 型チェック
mypy onsenpi

# リンター
ruff check onsenpi
```

## ライセンス

MIT License
