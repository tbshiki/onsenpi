# onsenpi

温泉（Onsen）のように、Amazon SP-APIを使いやすく、快適にするPythonラッパーライブラリ。

SP-API -> spapi -> spa + pi -> onsen + pi -> onsenpi

## 概要

onsenpiは開発者向けにAmazon Selling Partner API（SP-API）の使用を簡素化するライブラリです。
このライブラリはAPIとの対話をより直感的で扱いやすくすることで、開発効率を高めます。

## 最新情報（v0.2.6）
- **消し込みデータ（POST_FLAT_FILE_RECONCILIATION_DATA）API送信機能追加** - Amazonマーケットプレイスの消し込みデータをAPI経由で送信可能に

### 前回までのアップデート（～v0.2.5）

v0.2.5
- **APIリクエストのキャッシュ機能追加** - 同じリクエストが繰り返される場合の効率を大幅に向上
- **指数バックオフを使用したリトライ機能** - API制限やサーバーエラーからの復帰を自動化
- **アダプティブインターバル機能** - レポートステータス確認の間隔を動的に最適化
- **バッチ処理の強化** - 大容量ファイル処理のパフォーマンスを向上
- **型ヒントの完全対応** - PEP 561に準拠し、IDE開発体験を向上
- **Python 3.12のサポート追加** - 最新のPythonバージョンに対応
- **ダウンロード進捗表示の改善** - 大きなファイルのダウンロード状況を視覚化

v0.2.4
- メモリ効率の改善によるパフォーマンス最適化（大容量ファイル処理の効率化）
- 詳細なエラー診断機能の拡充（スロットリング検出、認証エラー識別）
- ログ設定のランタイム制御機能の追加
- TSVファイル操作ユーティリティの追加（マージ、列抽出）
- エラーハンドリングとロギングの統一化
- コンテキストマネージャとストリーミング処理の強化

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
- APIレスポンスのキャッシュ機能
- 指数バックオフを使用したリトライ機能

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
    seller_id='YOUR_SELLER_ID',  # 一部のAPIで必要な場合
    cache_size=128  # APIレスポンスのキャッシュサイズを設定（デフォルト: 128）
)

# ランタイムでのログレベル変更も可能
client.set_log_level(logging.DEBUG)  # 問題調査時に詳細ログに切り替え

# キャッシュをクリアする場合
client.clear_caches()  # 明示的に最新データを取得したい場合
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

# レポートが準備できるまで待機（アダプティブインターバルで効率的に待機）
document_id = client.inventory.wait_for_report_to_be_ready(
    report_id,
    timeout=300,              # 最大待機時間（秒）
    interval=30,              # 基本の確認間隔（秒）
    adaptive_interval=True    # 状況に応じて間隔を動的に調整
)

if document_id:
    print(f"ドキュメントID: {document_id}")

    # レポートをダウンロード（進捗表示付き）
    temp_gzip_file = "temp_report.gz"
    if client.inventory.download_report_data(document_id, temp_gzip_file):
        # ダウンロードしたGZIPファイルをテキストに変換（バッチ処理で効率化）
        from onsenpi import DataConverter
        DataConverter.convert_gzip_to_txt(temp_gzip_file, "report.txt", delete_original=True)
        print("レポートの変換が完了しました")

        # または、メモリ効率の良いストリーミング処理を使用（非常に大きなファイル向け）
        # DataConverter.convert_gzip_to_txt_streaming(temp_gzip_file, "report.txt", delete_original=True)
```

### 商品情報の検索（キャッシュ機能付き）

```python
# キーワードで商品カタログを検索（同一検索は自動的にキャッシュされる）
search_results = client.product.search_catalog_items("keyboard")
if search_results and "items" in search_results:
    print(f"検索結果: {len(search_results['items'])} 件")

    # 検索結果から最初のASINを取得
    if search_results['items']:
        asin = search_results['items'][0].get('asin')

        # 商品の詳細情報を取得（キャッシュされる）
        item_details = client.product.get_item(asin)
        print(f"商品名: {item_details.get('attributes', {}).get('title', 'Unknown')}")

        # 同じASINで再取得するとキャッシュから即時返却
        item_details_cached = client.product.get_item(asin)

        # キャッシュをクリアする場合
        # client.clear_caches()
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

### リトライ機能付きAPI呼び出し

```python
# リトライ機能を使用した堅牢な呼び出し
try:
    # 最大リトライ回数とリトライ前の待機秒数をカスタマイズ可能
    catalog_info = client.inventory.get_catalog_item(
        asin="B01234567",
        max_retries=5,          # 最大リトライ回数
        retry_delay=2           # 初回リトライ前の待機秒数（指数的に増加）
    )
    print(f"取得成功: {catalog_info.get('title', 'Unknown')}")
except Exception as e:
    print(f"最大リトライ後もエラー: {e}")
```

### 消し込みデータ（Reconciliation Feed）の送信

```python
from onsenpi import OnsenpiSPAPIClient
import logging

client = OnsenpiSPAPIClient(
    marketplace="JP",  # または Marketplaces.JP
    refresh_token="YOUR_REFRESH_TOKEN",
    lwa_app_id="YOUR_LWA_APP_ID",
    lwa_client_secret="YOUR_LWA_CLIENT_SECRET",
    seller_id="YOUR_SELLER_ID",
    log_level=logging.INFO,
)

tsv_path = "reconciliation.txt"  # タブ区切りテキストファイル

try:
    result = client.feeds.send_reconciliation_data(tsv_path)
    print("Feed送信成功:", result)
except Exception as e:
    print("Feed送信失敗:", e)
```

- `reconciliation.txt` はAmazon指定フォーマットのタブ区切りテキスト
- `client.feeds.send_reconciliation_data(tsv_path)` でAPI経由で送信
- エラー時は例外が発生するのでtry/exceptでハンドリング

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
# 型チェック
mypy onsenpi

# オプションのコード品質チェック（Ruffを使用）
ruff check onsenpi
```

## ライセンス

MIT License
