# onsenpi

温泉（Onsen）のように、Amazon SP-APIを使いやすく、快適にするPythonラッパーライブラリ。

SP-API -> spapi -> spa + pi -> onsen + pi -> onsenpi

## 概要

onsenpiは開発者向けにAmazon Selling Partner API（SP-API）の使用を簡素化するライブラリです。
このライブラリはAPIとの対話をより直感的で扱いやすくすることで、開発効率を高めます。

## 最新情報（v0.2.4）

- メモリ効率の改善によるパフォーマンス最適化（大容量ファイル処理の効率化）
- 詳細なエラー診断機能の拡充（スロットリング検出、認証エラー識別）
- ログ設定のランタイム制御機能の追加
- TSVファイル操作ユーティリティの追加（マージ、列抽出）
- エラーハンドリングとロギングの統一化
- コンテキストマネージャとストリーミング処理の強化

### 前回のアップデート（v0.2.3）

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
- 大容量ファイルの効率的な処理

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
    log_level=logging.INFO,  # ロギングレベルをカスタマイズ可能
    seller_id='YOUR_SELLER_ID'  # 一部のAPIで必要な場合
)

# ランタイムでのログレベル変更も可能
client.set_log_level(logging.DEBUG)  # 問題調査時に詳細ログに切り替え
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

    # スロットリングエラー（レート制限）の検出
    if e.is_throttling_error():
        print("レート制限に達しました。少し待ってから再試行してください。")
    # 認証エラーの検出
    elif e.is_authentication_error():
        print("認証情報に問題があります。リフレッシュトークンを確認してください。")
except OnsenpiValidationError as e:
    print(f"入力値検証エラー: {e}")
    print(f"エラー詳細: {e.get_error_details()}")
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

# 既存のロガーをクライアントに渡す
client = OnsenpiSPAPIClient(
    marketplace=Marketplaces.JP,
    refresh_token='YOUR_REFRESH_TOKEN',
    lwa_app_id='YOUR_LWA_APP_ID',
    lwa_client_secret='YOUR_LWA_CLIENT_SECRET',
    logger=logger
)
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
        # ダウンロードしたGZIPファイルをテキストに変換（通常のCSV処理）
        from onsenpi import DataConverter
        DataConverter.convert_gzip_to_txt(temp_gzip_file, "report.txt", delete_original=True)
        print("レポートの変換が完了しました")

        # または、メモリ効率の良いストリーミング処理を使用（非常に大きなファイル向け）
        # DataConverter.convert_gzip_to_txt_streaming(temp_gzip_file, "report.txt", delete_original=True)
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

### 大きなCSV/TSVファイルの効率的な処理

```python
from onsenpi import DataConverter

# 大きなCSV/TSVファイルをメモリ効率良く処理
file_path = "large_report.txt"

# イテレータを使った行単位の処理
for row in DataConverter.parse_csv_from_file(file_path, delimiter="\t"):
    # 各行を辞書としてアクセス可能
    sku = row.get("sku", "")
    asin = row.get("asin", "")
    if sku and asin:
        print(f"SKU: {sku}, ASIN: {asin}")
```

### TSVファイルの操作

```python
from onsenpi import DataConverter

# 複数のTSVファイルをマージ
source_files = ["report1.txt", "report2.txt", "report3.txt"]
merged_rows = DataConverter.merge_tsv_files(source_files, "merged_report.txt")
print(f"合計 {merged_rows} 行をマージしました")

# 特定の列のみを抽出
columns_to_extract = [0, 3, 5]  # 0、3、5列目（インデックスは0から開始）を抽出
processed_rows = DataConverter.extract_columns_from_tsv(
    "large_report.txt",
    "extracted_data.txt",
    columns_to_extract
)
print(f"{processed_rows} 行から指定した列を抽出しました")
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

# ディレクトリの安全な作成
try:
    DataConverter.ensure_directory_exists("data/reports")
    print("ディレクトリを作成しました")
except Exception as e:
    print(f"ディレクトリ作成エラー: {e}")

# ファイルの安全なコピー
try:
    DataConverter.safe_copy_file("source.txt", "backups/source_backup.txt")
    print("ファイルをコピーしました")
except Exception as e:
    print(f"ファイルコピーエラー: {e}")
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
# コード品質チェックとフォーマット (Ruff)
ruff check onsenpi tests
ruff format onsenpi tests

# 型チェック
mypy onsenpi
```

## ライセンス

MIT License
